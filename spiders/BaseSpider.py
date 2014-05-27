import re
import urllib
import urllib2
import urlparse
import threading
import Queue

class BaseSpider():
    def __init__(self):
        pass
    def request(self,url):
        pass
cnt=0
class Downloader(threading.Thread):
    
    user_agent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0) 32-bit IE on 64-bit Windows 7"
    headers={'User-Agent':user_agent}
    
    
    def __init__(self,queue,out_queue):
        threading.Thread.__init__(self)
        self.queue=queue
        self.out_queue=out_queue
        
    def run(self):
        while True:
            link=self.queue.get()
            req=urllib2.urlopen(link)
            repo=req.read()
            self.out_queue.put(repo)
            global cnt
            print "%d get the link:%s\n"%(cnt,link)
            cnt=cnt+1
            self.queue.task_done()
            
class Parse(threading.Thread):
    def __init__(self,queue,out_queue):
        threading.Thread.__init__(self)
        self.queue=queue
        self.out_queue=out_queue
        
    def run(self):
        while True:
            repo=self.out_queue.get()
            #print repo[0:50]
            self.out_queue.task_done()
            pattern=re.compile(r'<a\shref="(list[.]asp.*?)">')
            results= pattern.findall(repo)
            for result in results:
                #print result
                link= urlparse.urljoin("http://www.cc98.org",result)
                #self.queue.put(link)
                

tasks=["http://www.cc98.org/list.asp?boardid=2",
            "http://www.cc98.org/list.asp?boardid=3",
            "http://www.cc98.org/list.asp?boardid=4",
            "http://www.cc98.org/list.asp?boardid=5",
            "http://www.cc98.org/list.asp?boardid=6"]
queue=Queue.Queue()
out_queue=Queue.Queue()
for i in range(5):
    t=Downloader(queue,out_queue)
    t.setDaemon(True)
    t.start()
for task in tasks:
    queue.put(task)
for i in range(2):
    p=Parse(queue,out_queue)
    p.setDaemon(True)
    p.start()
    
queue.join()
out_queue.join()

    
    