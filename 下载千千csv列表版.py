# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 13:29:51 2020

@author: sds
"""

import re
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
'''
headers={
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Connection":"keep-alive",
    "Host":    "36kr.com/newsflashes",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:55.0) Gecko/20100101 Firefox/55.0"
}
'''
def get_html(artistid):
    api = 'http://music.taihe.com%s' %artistid
    #data = {'key': name}
    resp = requests.get(api,  headers=headers)
    resp.encoding = resp.apparent_encoding
    html = resp.text
    #print(html)
    return html



def get_songlist(html):
    
    soup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')

    sids =soup.find_all(attrs={"class": "icon-share iconfont"})
    
    #获取歌曲id
    #print(sids)
    #print(type(sids))
    rstr = r"[\/\\\:\*\?\"\<\>\|&@%$#]"
    i=1
    for sid in sids:
        print('----------')
        #print(sid)
        data_songid=sid.attrs.get('data-songid')
        data_title=sid.attrs.get('data-title')
        data_albumtitle=sid.attrs.get('data-albumtitle')
        data_author=sid.attrs.get('data-author')
        print(i)
        print('data-songid:',data_songid)
        print('data-title:',data_title)
        print('data-albumtitle:',data_albumtitle)
        print('data-author:',data_author)
        url=get_url(data_songid)
        filename = data_author+'_'+data_title
        filename=re.sub(rstr, "",filename)
        download(i,filename,url)
        i=i+1


def get_url(songid):
    #item = {}
    url = 'http://musicapi.taihe.com/v1/restserver/ting?method=baidu.ting.song.playAAC&format=jsonp&callback=jQuery17204869203719595674_1564707595390&songid=%s&from=web&_=1564707598783'%songid
    #url = 'http://musicapi.taihe.com/v1/restserver/ting?method=baidu.ting.song.playAAC&format=jsonp&callback=jQuery17204869203719595674_1564707595390&songid=210906&from=web&_=1564707598783'
    content1 = requests.get(url, headers=headers)
    #print(content1.raise_for_status())
    content1.encoding = content1.apparent_encoding
    #print(content1)
    content = content1.text
    
    
    #respone=requests.get(url,timeout=10,headers=headers)
    #respone=respone.json()
    
    #print(content)
    #js = json.loads(respone.text)
    #print (js)
    data1 = re.findall(r'\((.*)\);', content)
    #print(data1)
    try:
        data2 = json.loads(data1[0])
    except:
        data2=None
        print('json数据获取失败')
        time.sleep(5)

    #print(data2)
    #song_name = data2['songinfo']['title']
    #item['歌曲名字'] = song_name
    try:
        song_mp3_url = data2['bitrate']['file_link']
    except:
        song_mp3_url =None
        print('mp3下载地址获取失败')
        time.sleep(2)
    #item['歌曲地址'] = song_mp3_url
    #print('歌名为《%s》的音乐地址为:%s'% ( song_name, song_mp3_url))
    return song_mp3_url


def download(n,filename,url):
    #print(os.path.exists('%s.mp3' %filename))
    if os.path.exists('%s.mp3' %filename):
        print(filename,'已经存在')
    elif url==None:
        pass
    else:
        r = requests.get(url, stream=True, headers=headers)
        length = float(r.headers['content-length'])
        print('文件size：',length)
        f = open('%s.mp3' %filename, 'wb')
        count = 0
        count_tmp = 0
        time1 = time.time()
        print("正在下载第{0}首， 歌曲名为：《{1}》".format(n, filename))
        for chunk in r.iter_content(chunk_size = 512):
            if chunk:
                f.write(chunk)
                count += len(chunk)
                if time.time() - time1 > 2:
                    p = count / length * 100
                    speed = (count - count_tmp) / 1024 / 1024 / 2
                    count_tmp = count
                    print(filename + ': ' + formatFloat(p) + '%' + ' Speed: ' + formatFloat(speed) + 'M/S')
                    time1 = time.time()
        f.close()
        print("第{0}首： 《{1}》 已下载完毕".format(n, filename))
        time.sleep(2)

def formatFloat(num):
    return '{:.2f}'.format(num)

        
if __name__ == '__main__':
    i=1
    while True:
        read_csv=pd.read_csv('_1_artistid.csv', sep=',')
        #print(read_csv)
        artistid=read_csv['artistid'][0]
        artistname=read_csv['artistname'][0]
        print(artistid,artistname)
        html_content = get_html(artistid)
        get_songlist(html_content)
        print('已经下载了%s位歌手的歌曲'%str(i))
        read_csv.drop(0,inplace=True)
        read_csv.to_csv('_1_artistid.csv',index = False)
        
        time.sleep(1)




          
