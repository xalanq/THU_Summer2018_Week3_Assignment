import json
from django.core.management.base import BaseCommand
from django.db import transaction
from postdb.models import *
from thulac import thulac
import threading, queue

thu = thulac(seg_only=True, rm_space=True)

cnt_thread = 10
timeout = 10
q = queue.Queue()
mutex = threading.Lock()


class Command(BaseCommand):

    def is_biaodian(self, x):
        if x == '——':
            return True
        return x in r'''，。、；‘【】、·—《》？：“{}|,./;'[]\=-`<>?:"{}|_+~'''

    @transaction.atomic
    def go(self):
        all = PostInfo.objects.all().values_list('NID', 'title', 'TID')
        cnt = 0
        l = len(all)
        index_all = IndexInfo.objects.all()
        ci_all = {}
        ps_all = {}
        for t in index_all:
            ci_all[t.key] = json.loads(t.value)
        for t in all:
            ps_all[t[0]] = {'title': t[1], 'TID': t[2]}

        def work():
            nonlocal cnt, l, ci_all, ps_all
            while not q.empty():
                mutex.acquire()
                cnt += 1
                print('count {} / {}'.format(cnt, l))
                mutex.release()

                NID, title = q.get()
                ci = thu.cut(' '.join(title.split()))
                res = dict()
                for x in ci:
                    if self.is_biaodian(x[0]):
                        continue
                    try:
                        arr = ci_all[x[0]]
                        for _ in arr:
                            if _[1] == NID:
                                continue
                            if res.get(_[1]):
                                res[_[1]] += _[0]
                            else:
                                res[_[1]] = _[0]
                    except Exception as e:
                        pass
                mx_limit = 3
                ans = []
                for (x, y) in res.items():
                    if len(ans) < mx_limit:
                        ans.append([x, y])
                    else:
                        mn = 0
                        for j in range(1, mx_limit):
                            if ans[j][1] < ans[mn][1]:
                                mn = j
                        if y > ans[mn][1]:
                            ans[mn] = [x, y]
                ans.sort(key=lambda x: x[1], reverse=True)
                ans = [ps_all[ans[i][0]] for i in range(len(ans))]
                ans = json.dumps(ans)
                obj = None
                try:
                    obj = PostRelation.objects.get(NID=NID)
                    obj.relation = ans
                    obj.save()
                except Exception as e:
                    PostRelation.objects.create(NID=NID, relation=ans)
                q.task_done()

        for t in all:
            q.put((t[0], t[1]))

        for i in range(cnt_thread):
            threading.Thread(target=work()).start()

        q.join()

    def handle(self, *args, **options):
        self.go()
