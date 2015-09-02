# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from douban.items import DoubanItem


class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["book.douban.com"]
    start_urls = (
        'https://book.douban.com/top250',
    )

    rules = (
        # 列表页url
        Rule(LinkExtractor(allow=(r"https://book.douban.com/top250\?start=\d+"))),
        # 详情页url
        Rule(LinkExtractor(allow=(r"https://book.douban.com/subject/\d+")), callback="books_parse")
    )

    def books_parse(self, response):
        sel = Selector(response=response)
        item = DoubanItem()
        

        item["name"] = sel.xpath("//div[@id='wrapper']/h1/span/text()").extract()[0].strip()
        item["score"] = sel.xpath("//div[@class='rating_wrap']/p[1]/strong/text()").extract()[0].strip()
        item["link"] = response.url

        try:
            contents = sel.xpath("//div[@id='link-report']//div[@class='intro']")[-1].xpath(".//p//text()").extract()
            item["content_description"] = "\n".join(content for content in contents)
        except:
            item["content_description"] = ""
        try:
            profiles = sel.xpath("//div[@class='related_info']//div[@class='indent ']//div[@class='intro']")[-1].xpath(".//p//text()").extract()
            item["author_profile"] = "\n".join(profile for profile in profiles)
        except:
            item["author_profile"] = ""

        datas = response.xpath("//div[@id='info']//text()").extract()
        datas = [data.strip() for data in datas]
        datas = [data for data in datas if data != ""]
        for i, data in enumerate(datas):
            print "index %d " %i, data
        for data in datas:
            if u"作者" in data:
                if u":" in data:
                    item["author"] = datas[datas.index(data)+1]
                elif u":" not in data:
                    item["author"] = datas[datas.index(data)+2]
            # 找出版社中有个坑, 因为很多出版社名包含"出版社", 如: 上海译文出版社
            #elif u"出版社" in data:
            #    if u":" in data:
            #        item["press"] = datas[datas.index(data)+1]
            #    elif u":" not in data:
            #        item["press"] = datas[datas.index(data)+2]
            elif u"出版社:" in data:
                item["press"] = datas[datas.index(data)+1]
            elif u"出版年:" in data:
                item["date"] = datas[datas.index(data)+1]
            elif u"页数:" in data:
                item["page"] = datas[datas.index(data)+1]
            elif u"定价:" in data:
                item["price"] = datas[datas.index(data)+1]
            elif u"ISBN:" in data:
                item["ISBN"] = datas[datas.index(data)+1]

        #if "subject" in response.url:
        #    from scrapy.shell import inspect_response
        #    inspect_response(response, self)
        return item
