# -*- coding: utf-8 -*-
import scrapy, re, logging, time
from crawlers.items import CrawlersItem
from urllib.parse import urlparse
from scrapy_splash import SplashRequest
from scrapy.exceptions import CloseSpider
from crawlers import settings

crawled = []
class FirstCrawlerSpider(scrapy.Spider):
    name = "first-crawler"
    http_user ="9905a2023e37484985a3fa742aa36987"
    allowed_domains = []
    handle_httpstatus_all = True
    item_count = 0
    start_urls = []
    ss = None
    single_shop_regex = None
    via_page_url_regex = None
    script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:autoload("https://code.jquery.com/jquery-3.1.1.min.js"))
            assert(splash:go(url))
            assert(splash:wait(1))
            assert(splash:runjs(splash.args.script))
            assert(splash:wait(10))
            return {
                url = splash:url(),
                html = splash:html()
            }
        end
        """
    def __init__(self, sleep_time="", limit_number="", shops_root_url="", pagination_regex="", via_page_url_regex="", single_shop_regex="", *args, **kwargs):
        super(FirstCrawlerSpider, self).__init__(*args, **kwargs)
        if shops_root_url and single_shop_regex:
            self.limit_number = limit_number or None
            if sleep_time:
                self.download_delay = int(sleep_time)
            if pagination_regex:
                self.pagination_regex = re.compile(pagination_regex)
            else:
                self.pagination_regex = None
            self.start_urls.append(shops_root_url)
            self.single_shop_regex = [re.compile(l) for l in single_shop_regex.split(";")]
            if via_page_url_regex:
                self.via_page_url_regex = [re.compile(l) for l in via_page_url_regex.split(";")]
            else:
                self.via_page_url_regex = None

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse)

    def parse(self, response):
        url = None
        for href in response.xpath('//@href').extract():
            if href:
                url = response.urljoin(href)
                if self.via_page_url_regex:
                    for regex_1 in self.via_page_url_regex:
                        for regex_2 in self.single_shop_regex:
                            if url not in crawled and (regex_1.search(url) or regex_2.search(url)):
                                yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                            elif self.pagination_regex:
                                if self.pagination_regex.search(url):
                                    yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)

                elif self.pagination_regex:
                    if self.pagination_regex.search(url):
                        yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                    else:
                        for regex in self.single_shop_regex:
                            if regex.search(url):
                                yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                if self.single_shop_regex:
                    for regex in self.single_shop_regex:
                        if regex.search(url):
                            yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)

        for a in response.xpath('//*[@onclick]/@id').extract():
            yield SplashRequest(url=response.url, endpoint='execute', args={'url':response.url,'script':'$("#{}").click()'.format(a), 'lua_source':self.script}, callback=self.parse_js)

    def check_limit(self):
        if self.limit_number:
            if self.item_count >= int(self.limit_number):
                raise CloseSpider("Limit number reached")
        else:
            pass

    def parse_js(self, response):
        if response.url not in crawled:
            crawled.append(response.url)
            self.check_limit()
            match = False
            for regex in self.single_shop_regex:
                if regex.search(response.url):
                    match = True
                    item = CrawlersItem()
                    item['title'] = response.xpath('//title/text()').extract_first()
                    item['url'] = response.url
                    self.item_count+=1
                    yield item
                    break
            if not match:
                for href in response.xpath('//@href[not(contains(., ".css")) and not(contains(., ".ico")) and not(contains(.,".png")) and not(contains(.,".pdf"))]').extract():
                    url = response.urljoin(href)
                    if self.via_page_url_regex:
                        for regex_1 in self.via_page_url_regex:
                            for regex_2 in self.single_shop_regex:
                                if url not in crawled and (regex_1.search(url) or regex_2.search(url)):
                                    yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                                elif self.pagination_regex:
                                    if self.pagination_regex.search(url):
                                        yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                    else:
                        if self.pagination_regex:
                            if self.pagination_regex.search(url) and (url not in crawled):
                                yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                            else:
                                for regex in self.single_shop_regex:
                                    if url not in crawled and regex.search(url):
                                        yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
                        else:
                            for regex in self.single_shop_regex:
                                if url not in crawled and regex.search(url):
                                    yield SplashRequest(url, args={'wait':5}, endpoint="render.html", callback=self.parse_js)
