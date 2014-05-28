#!/usr/bin/python
# encoding=utf8

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

import os
import re
import urllib
import urllib2
import urlparse
import threading
import Queue
from time import sleep

"""
LinkType
    TaoBaoSearchPage=10
    TaoBaoItemPage=11
    
    JdSearchPage=20
    JdItemPage=21
    JdPricePage=22
    JdImagePage=23
    JdCommentsPage=24
    
parse_helper={20:[]}
"""


#global parameter
MAX_ITEM_CNT=5
MAX_COMM_CNT=5
DOWNLOAD_CNT=1
PARSE_CNT=1
class Spider():
    def __init__(self,keyword):
        self.req_queue=Queue.Queue()
        self.resp_queue=Queue.Queue()
        self.downloaders=[]
        self.parses=[]
        self.cnt=0
        for i in range(DOWNLOAD_CNT):
            t=Downloader(self)
            self.downloaders.append(t)
        for i in range(PARSE_CNT):
            p=Parse(self)
            self.parses.append(p)
        tasks=[LinkItem("http://search.jd.com/Search?keyword="+keyword+"&enc=utf8",LinkType.JdSearchPage),LinkItem("http://s.taobao.com/search?q="+keyword,LinkType.TaoBaoSearchPage)]
        for task in tasks:
            self.req_queue.put(task)
    def init_resource(self):
        """
        self.parse_helper={LinkType.JdSearchPage:[{"regex_str":'p-name[^<]*?<a\s.*href=["](.*?item.*?[.]html)["]\sonclick=[^>]*>\s*([\w\W]*?)</a>',"child_type":LinkType.JdItemPage,"follow":True},
                                                  {"regex_str":"","child_type":LinkType.JdPricePage,"follow":False},
                                                  {"regex_str":"","child_type":LinkType.JdImagePage,"follow":False}],
                           LinkType.JdItemPage:[{"regex_str":"","child_typr":LinkType.JdCommentsPage,"follow":False}]
                           }
        """
    def start(self):
        for download in self.downloaders:
            download.setDaemon(True)
            download.start()
        for parse in self.parses:
            parse.setDaemon(True)
            parse.start()
        self.req_queue.join()
        self.resp_queue.join()
class Downloader(threading.Thread):
    
    def __init__(self,spider):
        threading.Thread.__init__(self)
        self.spider=spider
        self.user_agent="111Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0) 32-bit IE on 64-bit Windows 7"
        self.headers={'User-Agent':self.user_agent}
    
    def run(self):
        while True:
            linkitem=self.spider.req_queue.get()
            req=urllib2.Request(linkitem.link,None,self.headers)
            #page=urllib2.urlopen(req).read()
            page=urllib.urlopen(linkitem.link).read()
            #print linkitem.link+"-----"+page[0:20]
            #page=urllib2.urlopen(linkitem.link).read()
            
            self.spider.resp_queue.put(DataItem(self.spider.cnt,linkitem.link_type,page,linkitem.link_item_id))
            print "%d get the link:%s\n"%(self.spider.cnt,linkitem.link)
            self.spider.cnt=self.spider.cnt+1
            self.spider.req_queue.task_done()

class Parse(threading.Thread):
    def __init__(self,spider):
        threading.Thread.__init__(self)
        self.spider=spider
        
    def run(self):
        while True:
            data_item=self.spider.resp_queue.get()
            self.spider.resp_queue.task_done()
            if os.path.exists("tmp/")==False:
                os.mkdir("tmp/")
            if os.path.exists("tmp/pages/")==False:
                os.mkdir("tmp/pages/")
            if os.path.exists("tmp/datas/")==False:
                os.mkdir("tmp/datas/")
            f=open("tmp/pages/"+str(data_item.link_id)+".htm","w")
            f.write(data_item.link_data)
            f.close()
            #print data_item.link_data[0:200]
            if data_item.link_type==LinkType.JdSearchPage:
                ptn_item=re.compile('p-name[^<]*?<a\s.*href=["](?P<link>.*?item.*?(?P<id>\d+)[.]html)["]\sonclick=[^>]*>\s*(?P<title>[\w\W]*?)</a>')
                rlt_item=ptn_item.findall(data_item.link_data)
                for rlt in rlt_item[0:MAX_ITEM_CNT]:
                    link=urlparse.urljoin("http://www.jd.com",rlt[0])
                    link_item_id=rlt[1]
                    link_item_title=rlt[2]
                    open("tmp/datas/"+str(link_item_id)+"_title.txt","w").write(re.compile('<[^>]*?>').sub("",link_item_title)) 
                    self.spider.req_queue.put(LinkItem(link,LinkType.JdItemPage,link_item_id))
                    self.spider.req_queue.put(LinkItem("http://p.3.cn/prices/mgets?skuids=J_"+str(link_item_id),LinkType.JdPricePage,link_item_id))
                ptn_img=re.compile('p-img[^<]*?<a\s.*href=["].*?item.*?(?P<id>\d+)[.]html["]\sonclick=[^>]*>[\s\S]*?lazyload=["](?P<img>.*?)["][\s\S]*?</a>')
                rlt_img=ptn_img.findall(data_item.link_data)
                for rlt in rlt_img[0:MAX_ITEM_CNT]:
                    link_item_id=rlt[0]
                    link_item_img=rlt[1]
                    open("tmp/datas/"+str(link_item_id)+"_img.txt","w").write(re.compile('<[^>]*?>').sub("",link_item_img)) 
            elif data_item.link_type==LinkType.JdPricePage:
                open("tmp/datas/"+str(data_item.link_item_id)+"_price.txt","w").write(re.compile('p["]:["](?P<price>[^"]*?)["]').search(data_item.link_data).group('price')) 
            elif data_item.link_type==LinkType.JdItemPage:
                pass
            elif data_item.link_type==LinkType.JdCommentsPage:
                pass
            elif data_item.link_type==LinkType.TaoBaoSearchPage:
                ptn_item=re.compile('lazyload=["](.*?)["][\s\S]*?<h3\sclass=["]summary["][\s\S]*?href=["](.*?id=(\d+))["][\s\S]*?title=["]([^"]*?)["][\s\S]*?price["]>.*?(\d+[.]?\d*)?<em[\s\S]*?user_number_id=(\d+)["]')
                rlt_items=ptn_item.findall(data_item.link_data)
                for rlt in rlt_items[0:MAX_ITEM_CNT]:
                    link_item_id=rlt[2]
                    link=rlt[1]
                    link_item_user_id=rlt[5]
                    open("tmp/datas/"+str(link_item_id)+"_title.txt","w").write(rlt[3])
                    open("tmp/datas/"+str(link_item_id)+"_img.txt","w").write(rlt[0])
                    open("tmp/datas/"+str(link_item_id)+"_price.txt","w").write(rlt[4])   
                    self.spider.req_queue.put(LinkItem(link,LinkType.TaoBaoItemPage,link_item_id))
                    self.spider.req_queue.put(LinkItem('http://rate.taobao.com/feedRateList.htm?userNumId='+str(link_item_user_id)+'&auctionNumId='+str(link_item_id)+'&siteID=1&currentPageNum=1',LinkType.TaoBaoCommentsPage,link_item_id))
            elif data_item.link_type==LinkType.TaoBaoItemPage:
                #print data_item.link_item_id
                #print data_item.link_data
                attributes=re.compile('attributes-list">(?P<attrlist>[\s\S]*?)</ul>').search(data_item.link_data).group('attrlist')
                open("tmp/datas/"+str(data_item.link_item_id)+"_attribute.txt","w").write(re.compile('<[^>]*?>').sub("",attributes))
            elif data_item.link_type==LinkType.TaoBaoCommentsPage:
                ptn_comm=re.compile('content["]:["]([^"]*?)["]')
                rlt_items=ptn_comm.findall(data_item.link_data)
                f=open("tmp/datas/"+str(data_item.link_item_id)+"_comments.txt","w")
                for rlt in rlt_items[0:MAX_COMM_CNT]:
                    f.write('"'+re.compile('<[^>]*?>').sub("",rlt)+'"')
                f.close()
                
        
class LinkType():
    TaoBaoSearchPage=10
    TaoBaoItemPage=11
    TaoBaoCommentsPage=12
       
    JdSearchPage=20
    JdItemPage=21
    JdPricePage=22
    JdImagePage=23
    JdCommentsPage=24

class LinkItem():
    def __init__(self,link,link_type,link_item_id=0):
        self.link=link
        self.link_type=link_type
        self.link_item_id=link_item_id
class DataItem():
    def __init__(self,link_id,link_type,link_data,link_item_id=0):
        self.link_id=link_id
        self.link_type=link_type
        self.link_data=link_data
        self.link_item_id=link_item_id
        
class RecordItem():
    def __init__(self,item_id,title,img_url,price,para,comm):
        self.item_id=item_id
        self.title=title
        self.img_url=img_url
        self.price=price
        self.para=para
        self.comm=comm

keyword="联想y460"
s=Spider(keyword)
s.start()
    
    