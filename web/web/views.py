from django.shortcuts import render
from django.http import JsonResponse
from postdb.models import *
from thulac import thulac
from datetime import datetime
import time
import json

thu = thulac(seg_only=True, rm_space=True)

category = {
    'gj': '国际',
    'sz': '时政',
    'js': '军事',
    'sh': '社会',
    'kj': '科技',
    'jy': '教育',
    'ty': '体育'
}

source = [
    ['people', '人民网'],
    ['xinhua', '新华网']
]


def get_source(x):
    for name in source:
        if x.startswith(name[0]):
            return name[1]


def index(request):
    return render(request, "index.html")


def post_info(request):
    TID = request.GET.get('id', '')
    if not TID:
        return render(request, 'error.html')
    data = None
    try:
        data = PostInfo.objects.get(TID=TID)
    except Exception as e:
        return render(request, 'error.html')
    return render(request, 'post.html', {
        'NID': data.NID,
        'title': data.title,
        'time': datetime.strftime(data.time, '%Y-%m-%d %H:%M'),
        'content': data.content,
        'source_link': data.sourceLink,
        'source_text': data.sourceText,
        'origin_url': data.url
    })


def search(request):
    s = request.GET.get('wd', '')
    if not s:
        return render(request, "index.html")
    bg = request.GET.get('bg', '')
    ed = request.GET.get('ed', '')
    return render(request, "search.html", {'wd': s, 'bg': bg, 'ed': ed})


def ajax_total(request):
    return JsonResponse({'total': PostInfo.objects.count()})


def ajax_index_category(request):
    return JsonResponse(category)


index_page_size = 10


def ajax_index_post(request):
    cat = request.GET.get('category', '')
    if not cat:
        return JsonResponse({})
    try:
        page = int(request.GET.get('page', '1'))
    except Exception as e:
        return JsonResponse({})
    page = min(page, 5)
    bg = (page - 1) * index_page_size
    ed = min(PostInfo.objects.count(), page * index_page_size)
    data = PostInfo.objects.filter(category=category.get(cat, '国际')).order_by('-time').values_list('TID', 'title', 'time')[bg:ed]
    ret = dict()
    ret['len'] = len(data)
    cnt = 0
    for i in data:
        ret[cnt] = {
            'TID': i[0],
            'title': i[1],
            'time': datetime.strftime(i[2], '%Y/%m/%d %H:%M'),
            'source': get_source(i[0])
        }
        cnt += 1

    return JsonResponse(ret)


def is_biaodian(x):
    if x == '——':
        return True
    return x in r'''，。、；‘【】、·—《》？：“{}|,./;'[]\=-`<>?:"{}|_+~'''


def ajax_search(request):
    s = request.GET.get('wd', '')
    if not s:
        return JsonResponse({})
    bg = request.GET.get('bg', '')
    ed = request.GET.get('ed', '')
    if not bg or not ed:
        bg = ed = ''
    if bg and ed:
        try:
            bg = datetime.strptime(bg, '%Y-%m-%d')
            ed = datetime.strptime(ed, '%Y-%m-%d')
        except Exception as e:
            return JsonResponse({})
    if not bg and bg > ed:
        return JsonResponse({})

    startTime = time.time()
    ci = thu.cut(' '.join(s.split()))
    rci = []
    res = dict()
    for x in ci:
        if is_biaodian(x[0]):
            continue
        rci.append(x[0])
        arr = []
        try:
            arr = json.loads(IndexInfo.objects.get(key=x[0]).value)
            for _ in arr:
                if bg:
                    tm = datetime.strptime(_[2], '%Y-%m-%d-%H-%M-%S')
                    if tm < bg or tm > ed:
                        continue
                if res.get(_[1]):
                    res[_[1]] += _[0]
                else:
                    res[_[1]] = _[0]
        except Exception as e:
            pass
    res = list(res.items())
    res.sort(key=lambda x: x[1], reverse=True)
    res = [res[i][0] for i in range(len(res))]
    return JsonResponse({'len': len(res), 'cost': '{:.5f}'.format(time.time() - startTime), 'ci': rci, 'data': res})


def ajax_post_brief(request):
    l = len(request.GET)
    if not l:
        return JsonResponse({})
    data = dict()
    try:
        for i in range(l):
            x = request.GET.get(str(i))
            tmp = PostInfo.objects.get(NID=x)
            data[i] = {
                'TID': tmp.TID,
                'title': tmp.title,
                'brief': str(tmp.plain)[:100],
                'time': tmp.time.strftime('%Y/%m/%d %H:%M'),
                'source': get_source(tmp.TID),
            }
    except Exception as e:
        return JsonResponse({})
    return JsonResponse(data)


def ajax_post_relation(request):
    NID = request.GET.get('id', '')
    if not NID:
        return JsonResponse({'data': {}})
    data = None
    try:
        data = json.loads(PostRelation.objects.get(NID=NID).relation)
    except Exception as e:
        return JsonResponse({'data': {}})
    return JsonResponse({'data': data})

