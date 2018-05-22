# coding:utf-8
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import urllib2
import json
import re

# Create your views here.


def city_to_code(depart_city_name, arrive_city_name):
    """
    把下拉框选择的城市转化为对应缩写
    :param depart_city_name: 出发城市
    :param arrive_city_name: 到达城市
    :return: 城市编码
    """
    # <type 'unicode'> (u'\u5317\u4eac', u'\u4e0a\u6d77')
    depart_city_name = depart_city_name.encode('utf-8')
    arrive_city_name = arrive_city_name.encode('utf-8')
    # <type 'str'> ('\xe5\x8c\x97\xe4\xba\xac', '\xe4\xb8\x8a\xe6\xb5\xb7')
    dict_citys = {}
    with open('app/others/city.json') as file_object:
        contents = file_object.read()
        # p1 = r"(?<=\|).+[^\u4E00-\u9FA5]?(?=\()"  #  ?<=\|:以|开头(不含|) ?=\|:以|开结尾(不含|)
        p1 = r"(?<=\|).+(?=\")"  # 上海(SHA)|2|SHA 上海(浦东国际机场)(PVG)|2|SHA,PVG
        pattern1 = re.compile(p1)
        p11 = r".+[^\u4E00-\u9FA5]?(?=\()"  # 上海 上海(浦东国际机场)
        pattern11 = re.compile(p11)
        p12 = r"(?<=\|)[A-Z].+"  # SHA SHA,PVG
        pattern12 = re.compile(p12)
        citys = pattern1.findall(contents)
        for city in citys:
            cityname = re.search(pattern11, city).group(0)
            citycode = re.search(pattern12, city).group(0)
            dict_citys[cityname] = citycode
    depart_city_code = dict_citys[depart_city_name]
    arrive_city_code = dict_citys[arrive_city_name]
    return depart_city_code, arrive_city_code


def message(request):
    """
    该函数主要功能：1.接受页面post过来的查询参数，2.根据参数拼接所需的爬取数据的url，3.爬到数据后筛选出所需信息存入到list里，4.然后通过字典格式的返回到页面上
    :param request:
    :return:
    """
    if request.method == 'POST':
        # 1.页面post传过来的查询参数
        depart_city = request.POST.get('depart_city')
        arrive_city = request.POST.get('arrive_city')
        depart_date = request.POST.get('depart_date')
        end_time = request.POST.get('end_time')
        # subject = request.POST.get('subject')
        priority = request.POST.get('priority') # 成本性 时效性 晚点率


        # 将传过来的城市名字转换为城市缩写，如：北京->BJS，上海->SHA
        depart_city_code, arrive_city_code = city_to_code(depart_city, arrive_city)
        # 2.拼接爬取数据所需的url
        url = "http://flights.ctrip.com/domesticsearch/search/SearchFirstRouteFlights?DCity1=%s&ACity1=%s&SearchType=S&DDate1=%s" % (depart_city_code, arrive_city_code, depart_date)
        print url
        headers = {
            'Host': "flights.ctrip.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
            'Referer': url
        }
        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req)
        content = res.read()
        dict_content = json.loads(content, encoding="gbk")
        length = len(dict_content['fis'])
        print length
        list_all = []  #
        # 3.筛选数据所需信息存入到list里
        for i in range(length):
            # 循环遍历爬取的每一条信息
            if (dict_content['fis'][i][u'lp'] < 1000000):
                air_number = dict_content['fis'][i][u'fn']  # 航班号
                depart_city = dict_content['fis'][i][u'dpbn']  # 出发城市
                depart_time = dict_content['fis'][i][u'dt']  # 出发时间
                arrive_city = dict_content['fis'][i][u'apbn']  # 到达城市
                arrive_time = dict_content['fis'][i][u'at']  # 到达时间
                price = dict_content['fis'][i][u'lp']  # 机票价格
                HistoryPunctualityArr = json.loads(dict_content['fis'][i][u'confort'])['HistoryPunctualityArr']  # 晚点率
                # 把一条数据的机票价格，出发城市，出发时间，到达城市，到达时间存入到list_mess里
                list_mess = [air_number, depart_city, depart_time, arrive_city, arrive_time, price, HistoryPunctualityArr]
                # 把整条信息list_mess存入到list_all里
                list_all.append(list_mess)

        # TODO: 根据priority成本性 时效性 晚点率 处理数据
        if '成本性' in priority and '时效性' in priority and '晚点率' in priority:
            print 3
        else:
            if '成本性' in priority:
                print '1'
            if '时效性' in priority:
                print '2'
            if '晚点率' in priority:
                print '3'

        # 4.把list_all做成字典格式数据，并通过HttpResponse返回到页面
        mydict = {'list_all': list_all}
        return HttpResponse(json.dumps(mydict))
    return render(request,'message.html')


