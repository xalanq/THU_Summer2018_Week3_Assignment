from bs4 import BeautifulSoup
from datetime import datetime
from threading import Lock

mutex = Lock()


class AdapterXinhua:
    def __init__(self):
        self.clear()

    def clear(self):
        self.name = 'xinhua'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        }
        self.links = set()
        self.linksPos = 0
        self.initCnt = 0
        self.category = {
            0: '国际',
            1: '时政',
            2: '军事',
            3: '科技'
        }
        self.hostList = [
            'http://www.xinhuanet.com/world',
            'http://www.xinhuanet.com/politics',
            'http://www.xinhuanet.com/mil',
            'http://www.xinhuanet.com/tech',
            'http://www.xinhuanet.com/',
            'http://www.xinhuanet.com/world/hqlft2017/',
            'http://www.xinhuanet.com/world/hqgc.htm',
            'http://www.xinhuanet.com/world/wmyl.htm',
            'http://www.xinhuanet.com/politics/xgc.htm',
            'http://www.xinhuanet.com/politics/ytgz.htm',
            'http://www.xinhuanet.com/politics/szzt.htm',
            'http://www.xinhuanet.com/tech/hlwj.htm',
            'http://www.xinhuanet.com/tech/Eyt.htm',
            'http://www.xinhuanet.com/tech/wgc.htm',
            'http://www.xinhuanet.com/tech/ijm.htm',
            'http://www.xinhuanet.com/tech/sxj.htm',
            'http://www.xinhuanet.com/tech/cyb.htm',
            'http://www.xinhuanet.com/tech/5gsd/index.htm'
        ]
        self.initCntLimit = len(self.hostList)
        # self.initCntLimit = 1
        self.validCnt = 0
        self.existLinks = set()

    def addValidLink(self, link):
        self.existLinks.add(link)

    def host(self, op):
        return self.hostList[op]

    def init(self, op, text):
        def strip(x):
            ps = x.find('#')
            if ps != -1:
                x = x[:ps]
            ps = x.find('?')
            if ps != -1:
                x = x[:ps]
            return x

        bs = BeautifulSoup(text, 'html.parser')
        for lks in bs.find_all('a'):
            lk = str(lks.get('href'))
            if lk.startswith(self.host(0) + '/2018') or \
               lk.startswith(self.host(1) + '/2018') or \
               lk.startswith(self.host(2) + '/2018'):
                lk = strip(lk)
                if lk not in self.existLinks:
                    self.links.add(lk)

    def hasNextInit(self):
        return self.initCnt < self.initCntLimit

    def nextInitParam(self):
        self.initCnt += 1
        return 0, self.host(self.initCnt - 1), self.headers, {}

    def eval(self, op, text):
        # title, stamp, content, category, source, url
        data = dict()
        bs = BeautifulSoup(text, 'html.parser')

        def escape(x):
            x = x.replace(u'\xa0', u' ')
            x = x.replace(u'\u3000', u' ')
            x = x.strip()
            return x

        def parseContent(x):
            bg = x.find('<p')
            ed = x.rfind('</p>')
            if bg == -1:
                return x
            ed += 4
            return x[bg:ed]

        cat = 0
        for i in range(len(self.category)):
            if self.links[op].startswith(self.host(i)):
                cat = i
                data['category'] = self.category[i]

        a = None

        if cat in [0, 1]:
            a = bs.find('div', attrs={'class': 'h-title'})
        elif cat == 2:
            a = bs.find('h1', attrs={'id': 'title'})
        if a:
            data['title'] = escape(a.text)

        if cat in [0, 1]:
            a = bs.find('span', attrs={'class': 'h-time'})
        elif cat == 2:
            a = bs.find('span', attrs={'class': 'time'})
        if a:
            if cat in [0, 1]:
                a = datetime.strptime(escape(a.text), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            elif cat == 2:
                a = datetime.strptime(escape(a.text), '%Y年%m月%d日 %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            data['stamp'] = a

        a = bs.find('em', attrs={'id': 'source'})
        if a:
            data['source'] = {'link': '', 'text': escape(a.text)}

        if cat in [0, 1]:
            a = bs.find('div', attrs={'id': 'p-detail'})
        elif cat == 2:
            a = bs.find('div', attrs={'class': 'article'})
        if a and ''.join(a.text.split()):
            data['content'] = parseContent(str(a))

        ID = None
        if 'content' in data and data['content']:
            mutex.acquire()
            self.validCnt += 1
            ID = self.name + '_' + str(len(self.existLinks) + self.validCnt)
            mutex.release()

        data['url'] = self.links[op]

        return ID, data

    def hasNext(self):
        if self.linksPos == 0:
            self.links = list(self.links)
            self.validCnt = 0
        return self.linksPos < len(self.links)

    def nextParam(self):
        self.linksPos += 1
        return self.linksPos - 1, self.links[self.linksPos - 1], self.headers, {}

    def encoding(self):
        return "utf-8"
