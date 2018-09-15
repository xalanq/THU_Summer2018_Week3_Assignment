from bs4 import BeautifulSoup
from datetime import datetime
from threading import Lock

mutex = Lock()

class AdapterPeople:
    def __init__(self):
        self.clear()

    def clear(self):
        self.name = 'people'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        }
        self.links = set()
        self.linksPos = 0
        self.initCnt = 0
        self.category = {
            0: '国际',
            1: '军事',
            2: '时政',
            3: '社会',
            4: '科技',
            5: '教育',
            6: '体育',
        }
        self.hostList = [
            ['http://world.people.com.cn', 5, 0],
            ['http://military.people.com.cn', 1, 1],
            ['http://politics.people.com.cn', 6, 2],
            ['http://society.people.com.cn', 10, 3],
            ['http://scitech.people.com.cn', 12, 4],
            ['http://edu.people.com.cn', 1, 5],
            ['http://sports.people.com.cn', 1, 6],
            ['http://www.people.com.cn', 1, -1],
        ]
        '''
            ['http://military.people.com.cn/GB/172467', 6, 1],
            ['http://scitech.people.com.cn/GB/53752', 7, 4],
            ['http://scitech.people.com.cn/GB/1056', 7, 4],
            ['http://scitech.people.com.cn/GB/25892', 7, 4],
            ['http://scitech.people.com.cn/GB/25895', 7, 4],
            ['http://scitech.people.com.cn/GB/41163', 7, 4],
            ['http://scitech.people.com.cn/GB/1057', 7, 4],
            ['http://scitech.people.com.cn/GB/59405', 7, 4],
            ['http://society.people.com.cn/GB/1062', 5, 3],
            ['http://society.people.com.cn/GB/41158', 5, 3],
            ['http://military.people.com.cn/GB/52963', 7, 1],
            ['http://military.people.com.cn/GB/172467', 7, 1],
            ['http://military.people.com.cn/GB/367527', 7, 1],
            ['http://military.people.com.cn/GB/1077', 7, 1],
            ['http://world.people.com.cn/GB/107182', 1, 0]
            ['http://edu.people.com.cn/GB/1053', 7, 5],
            ['http://edu.people.com.cn/GB/367001', 10, 5],
            ['http://edu.people.com.cn/GB/gaokao', 1, 5],
            ['http://edu.people.com.cn/GB/226718', 7, 5],
            ['http://edu.people.com.cn/GB/227057', 7, 5],
            ['http://edu.people.com.cn/GB/227065', 7, 5],
            ['http://edu.people.com.cn/GB/208610', 7, 5],
            ['http://edu.people.com.cn/GB/208610', 7, 5],
            ['http://sports.people.com.cn/GB/401891', 10, 6],
            ['http://sports.people.com.cn/GB/407727', 10, 6],
            ['http://sports.people.com.cn/GB/22176', 4, 6],
            ['http://sports.people.com.cn/GB/35862', 4, 6],
        '''
        self.validCnt = 0
        self.existLinks = set()
        self.existHostLink = set()
        for i in self.hostList:
            self.existHostLink.add(i[0])

    def addValidLink(self, link):
        self.existLinks.add(link)

    def host(self, op):
        return self.hostList[op][0]

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
        if len(self.links) > 25000:
            return
        for lks in bs.find_all('a'):
            lk = str(lks.get('href'))
            if lk.startswith('/n1/') or lk.startswith('/n2/'):
                lk = self.host(op) + lk
                lk = strip(lk)
                if lk not in self.existLinks:
                    self.links.add(lk)
            else:
                for i in self.category.keys():
                    if lk.startswith(self.host(i) + '/n1/') or lk.startswith(self.host(i) + '/n2/'):
                        lk = strip(lk)
                        if lk not in self.existLinks:
                            self.links.add(lk)
                    elif lk.startswith(self.host(i) + '/GB/'):
                        lk = '/'.join(lk.split('/')[:-1])
                        if lk not in self.existHostLink:
                            self.existHostLink.add(lk)
                            self.hostList.append([lk, 10, i])

    def hasNextInit(self):
        limit = 0
        for i in range(len(self.hostList)):
            limit += self.hostList[i][1]
        return self.initCnt < min(2000, limit)

    def nextInitParam(self):
        self.initCnt += 1
        sum = 0
        for i in range(len(self.hostList)):
            x = self.hostList[i]
            sum += x[1]
            if self.initCnt <= sum:
                lk = x[0]
                if self.initCnt - (sum - x[1]) == 1:
                    lk += '/index.html'
                else:
                    lk += '/index{}.html'.format(self.initCnt - (sum - x[1]))
                return x[2], lk, self.headers, {}

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
        for i in self.category.keys():
            if self.links[op].startswith(self.host(i)):
                data['category'] = self.category[i]

        a = bs.find('h1')
        if a:
            data['title'] = escape(a.text)

        a = bs.find('div', attrs={'class': 'box01'})
        if a:
            b = a.find('div', attrs={'class': 'fl'})
            if b:
                dt = b.text[:16]
                dt = datetime.strptime(dt, '%Y年%m月%d日%H:%M').strftime('%Y-%m-%d %H:%M:%S')
                data['stamp'] = dt
            b = a.find('a')
            if b:
                data['source'] = {'link': b.get('href'), 'text': escape(b.text)}

        a = bs.find('div', attrs={'class': 'box_con'})
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
        return "GB2312"
