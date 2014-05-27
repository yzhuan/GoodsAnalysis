from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from Goods.items import *

import hashlib

class JdSpider(CrawlSpider):
    name="jd"
    allowed_domains=["jd.com"]
    start_urls=["http://search.jd.com/Search?keyword=小米手机&enc=utf-8"]
    rules=(Rule(SgmlLinkExtractor(allow=("list.asp")),follow=True),Rule(SgmlLinkExtractor(allow=("dispbbs.asp")),callback="parse_items",follow=False))

    def parse_items(self,response):
        hxs=HtmlXPathSelector(response)
        item=CC98Item()
        item["title"]=hxs.select("//title/text()").extract()
        item["link"]=response.url
        return item
