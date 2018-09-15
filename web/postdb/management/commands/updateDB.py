import json
from datetime import datetime
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from postdb.models import *
import thulac


class Command(BaseCommand):
    names = [
        'people',
        'xinhua'
    ]

    path = '../scraper/'

    thu = thulac.thulac(seg_only=True, rm_space=True)
    idx = dict()

    def fenci(self, NID, time, text, title):
        b = dict()

        def gg(t, g):
            data = self.thu.cut(t)
            for _ in data:
                x = _[0]
                a = b.get(x)
                if not a:
                    b[x] = g
                else:
                    b[x] += g

        gg(text, 1)
        gg(title, 50)

        print('NID: {}, len(word): {}'.format(NID, len(b)))
        for (x, y) in b.items():
            a = self.idx.get(x)
            t = [y, NID, time]
            if not a:
                self.idx[x] = [t]
            else:
                self.idx[x].append(t)

    @transaction.atomic
    def go(self):
        for name in self.names:
            print("====== start {} ======".format(name))
            filename = self.path + name + '.json'
            all = dict()
            try:
                f = open(filename, 'r')
                all = json.loads(f.read())
                print('Count: ', all['count'])
                f.close()
            except Exception as e:
                print(e)
                continue
            info = None
            try:
                info = WebInfo.objects.get(name=name)
            except Exception as e:
                print(e)
            cnt = 0
            if info:
                cnt = info.count
            tot = PostInfo.objects.count()

            for (TID, tmp) in all['data'].items():
                ID = int(TID.split('_')[-1])
                if ID <= cnt:
                    continue
                print('excuting {} / {}'.format(TID, all['count']))
                try:
                    cnt += 1
                    tot += 1
                    NID = tot
                    time = datetime.strptime(tmp.get('stamp', ''), '%Y-%m-%d %H:%M:%S')
                    title = tmp.get('title', '')
                    content = tmp.get('content', '')
                    bs = BeautifulSoup(content, 'html.parser')
                    plain = ' '.join(bs.get_text().split())
                    self.fenci(NID, datetime.strftime(time, '%Y-%m-%d-%H-%M-%S'), plain, title)

                    data = PostInfo()
                    data.NID = NID
                    data.TID = TID
                    data.time = time
                    data.category = tmp.get('category', '')
                    data.title = title
                    data.content = content
                    data.plain = plain
                    data.url = tmp.get('url', '')
                    source = tmp.get('source')
                    if source:
                        data.sourceLink = source.get('link', '')
                        data.sourceText = source.get('text', '')
                    data.save()
                except Exception as e:
                    print(e)
                    tot -= 1
                    cnt -= 1

            if info:
                info.count = cnt
                info.save()
            else:
                WebInfo.objects.create(name=name, count=cnt)

        print('====== building index ======')
        print('len:', len(self.idx))
        cnt = 0
        for (x, y) in self.idx.items():
            cnt += 1
            print('count: {} / {}'.format(cnt, len(self.idx)))
            obj = None
            arr = []
            try:
                obj = IndexInfo.objects.get(key=x)
                arr = json.loads(obj.value)
            except Exception as e:
                pass
            arr.extend(y)
            if obj:
                obj.value = json.dumps(arr)
                obj.save()
            else:
                IndexInfo.objects.create(key=x, value=json.dumps(arr))

    def handle(self, *args, **options):
        self.go()

