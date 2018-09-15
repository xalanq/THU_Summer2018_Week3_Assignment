import requests
import json
import threading, queue
import adapters

cnt_thread = 10
timeout = 10
q = queue.Queue()
mutex = threading.Lock()


def work(adapter, all):
    s = requests.session()

    while adapter.hasNextInit():
        q.put(adapter.nextInitParam())

    def initWork():
        while not q.empty():
            op, url, headers, params = q.get()

            mutex.acquire()
            print('search in: ', url)
            mutex.release()
            try:
                raw = s.get(url, params=params, headers=headers, timeout=timeout)
                raw.encoding = adapter.encoding()
                adapter.init(op, raw.text)
            except Exception as e:
                print('*** search {} Error!!! {}'.format(url, e))

            q.task_done()
            mutex.acquire()
            if adapter.hasNextInit():
                q.put(adapter.nextInitParam())
            mutex.release()

    for i in range(cnt_thread):
        threading.Thread(target=initWork).start()

    q.join()

    print('total link: ', len(adapter.links))

    while adapter.hasNext():
        q.put(adapter.nextParam())

    cnt = 0

    def collectWork():
        while not q.empty():
            nonlocal cnt
            op, url, headers, params = q.get()

            mutex.acquire()
            cnt += 1
            num = cnt
            print('collect No.{}: {}'.format(num, url))
            mutex.release()
            try:
                raw = s.get(url, params=params, headers=headers, timeout=timeout)
                raw.encoding = adapter.encoding()
                ID, data = adapter.eval(op, raw.text)
                if ID:
                    all['data'][ID] = data
            except Exception as e:
                print('*** collect No.{} Error!!! {}'.format(num, e))

            q.task_done()

    for i in range(cnt_thread):
        threading.Thread(target=collectWork).start()

    q.join()

    print("valid link: ", adapter.validCnt)
    all['count'] = len(adapter.existLinks) + adapter.validCnt


def main():
    for x in adapters.getAdapters():
        print('============ starting {} ============'.format(x.name))
        f = None
        all = dict()
        try:
            f = open(x.name + '.json', 'r')
            all = json.loads(f.read())
            print('Already count: ', all['count'])
            f.close()
        except Exception as e:
            print('err: ', e)
            all = {
                'name': x.name,
                'count': 0,
                'data': {}
            }
        for d in all['data'].values():
            x.addValidLink(d['url'])
        work(x, all)
        f = open(x.name + '.json', 'w')
        json.dump(all, f)
        print('\n\n')


if __name__ == '__main__':
    main()