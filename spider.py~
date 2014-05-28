#!/usr/local/bin/python
# coding: utf8

import os
import re
import urllib
import urllib2
import urlparse
import threading
import Queue


class Spider():
    def __init__(self,keyword):
        self.req_queue=Queue.Queue()
        self.resp_queue=Queue.Queue()
        self.downloaders=[]
        self.parses=[]
        self.cnt=0
        for i in range(5):
            t=Downloader(self)
            self.downloaders.append(t)
        for i in range(2):
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
        self.user_agent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0) 32-bit IE on 64-bit Windows 7"
        self.headers={'User-Agent':self.user_agent}
    
    def run(self):
        while True:
            linkitem=self.spider.req_queue.get()
            req=urllib2.Request(linkitem.link,None,self.headers)
            repo=urllib2.urlopen(req)
            page=repo.read()
            self.spider.resp_queue.put(DataItem(self.spider.cnt,linkitem.link_type,page))
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
            f=open("tmp/pages/"+str(data_item.link_id)+".htm","w")
            f.write(data_item.link_data)
            f.close()
            
            if data_item.link_type==LinkType.JdSearchPage:
                ptn_item=re.compile('p-name[^<]*?<a\s.*href=["](.*?item.*?[.]html)["]\sonclick=[^>]*>\s*([\w\W]*?)</a>')
                rlt_item=ptn_item.findall(data_item.link_data)
                for rlt in rlt_item:
                    link=urlparse.urljoin("http://www.jd.com",rlt[0])
                    self.spider.req_queue.put(LinkItem(link,LinkType.JdItemPage))
            elif data_item.link_type==LinkType.JdPricePage:
                pass
            elif data_item.link_type==LinkType.JdItemPage:
                pass
            elif data_item.link_type==LinkType.JdCommentsPage:
                pass
            elif data_item.link_type==LinkType.TaoBaoSearchPage:
                pass
            elif data_item.link_type==LinkType.TaoBaoItemPage:
                pass
            pattern=re.compile(r'<a\shref="(list[.]asp.*?)">')
            results= pattern.findall(data_item.link_data)
            for result in results:
                #print result
                link= urlparse.urljoin("http://www.cc98.org",result)
                #self.spider.req_queue.put(link)
                
        
class LinkType():
    TaoBaoSearchPage=10
    TaoBaoItemPage=11
   
    JdSearchPage=20
    JdItemPage=21
    JdPricePage=22
    JdImagePage=23
    JdCommentsPage=24

class LinkItem():
    def __init__(self,link,link_type):
        self.link=link
        self.link_type=link_type
class DataItem():
    def __init__(self,link_id,link_type,link_data):
        self.link_id=link_id
        self.link_type=link_type
        self.link_data=link_data
        
class RecordItem():
    def __init__(self,item_id,title,img_url,price,para,comm):
        self.item_id=item_id
        self.title=title
        self.img_url=img_url
        self.price=price
        self.para=para
        self.comm=comm

keyword=u"联想y460"
s=Spider(keyword)
s.start()
    
    
