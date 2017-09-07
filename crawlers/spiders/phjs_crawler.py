# -*- coding: utf-8 -*-
import scrapy, re, logging, time
from crawlers.items import CrawlersItem
from urllib.parse import urlparse
from selenium import webdriver
from scrapy.exceptions import CloseSpider
from crawlers import settings

crawled = []
class PhjsCrawlerSpider(scrapy.Spider):
    name = "phjs-crawler"
    http_user ="9905a2023e37484985a3fa742aa36987"
    allowed_domains = []
    item_count = 0
    start_urls = []
    single_shop_regex = None
    via_page_url_regex = None

    def __init__(self, sleep_time="", limit_number="", shops_root_url="", via_page_url_regex="", single_shop_regex="", *args, **kwargs):
        super(PhjsCrawlerSpider, self).__init__(*args, **kwargs)
        if shops_root_url and single_shop_regex:
            if limit_number:
                self.limit_number = limit_number
            if sleep_time:
                self.download_delay = int(sleep_time)
            self.start_urls.append(shops_root_url)
            parsed_uri = urlparse(shops_root_url)
            self.single_shop_regex = [re.compile(l) for l in single_shop_regex.split(";")]
            if via_page_url_regex:
                self.via_page_url_regex = [re.compile(l) for l in via_page_url_regex.split(";")]
            else:
                self.via_page_url_regex = None

    def parse(self, response):
        """driver = webdriver.PhantomJS()
        driver.get(response.url)
        url = None
        for href in driver.find_elements_by_xpath('//*[@href]'):
            if href.get_attribute('href'):
                url = response.urljoin(href.get_attribute('href'))
                if self.via_page_url_regex:
                    for regex_1 in self.via_page_url_regex:
                        for regex_2 in self.single_shop_regex:
                            if url not in crawled and (regex_1.search(url) or regex_2.search(url)):
                                yield scrapy.Request(url, callback=self.parse_js)
                else:
                    for regex in self.single_shop_regex:
                        if regex.search(url):
                            yield scrapy.Request(url, callback=self.parse_js)
        counter = 0
        for a in driver.find_elements_by_xpath('//*[@onclick]'):
            clickdriver = webdriver.PhantomJS()
            clickdriver.get(response.url)
            clickdriver.find_elements_by_xpath('//*[@onclick]')[counter].click()
            if len(clickdriver.window_handles)>1:
                clickdriver.switch_to_window(clickdriver.window_handles[1])
                yield scrapy.Request(url=clickdriver.current_url, callback=self.parse_js)
                clickdriver.close()
                clickdriver.switch_to_window(clickdriver.window_handles[0])
                clickdriver.close()
            else:
                yield scrapy.Request(url=clickdriver.current_url, callback=self.parse_js)
                clickdriver.close()
            counter+=1"""
        yield scrapy.Request("http://www.saizeriya.co.jp/restaurant/search_map.php?area1=5", callback=self.parse_js)

    def check_limit(self):
        if self.limit_number:
            if self.item_count >= int(self.limit_number):
                raise CloseSpider("Limit number reached")
        else:
            pass

    def parse_js(self, response):
        crawled.append(response.url)
        driver = webdriver.PhantomJS()
        driver.get(response.url)
        self.check_limit()
        match = False
        for regex in self.single_shop_regex:
            if regex.search(response.url):
                match = True
                item = CrawlersItem()
                item['title'] = driver.find_element_by_xpath('//title').get_attribute('innerHTML')
                item['url'] = response.url
                self.item_count+=1
                yield item
        if not match:
            for href in driver.find_elements_by_xpath('//*[@href[not(contains(., ".css")) and not(contains(., ".ico")) and not(contains(.,".png")) and not(contains(.,".pdf"))]]'):
                url = response.urljoin(href.get_attribute('href'))
                if self.via_page_url_regex:
                    for regex_1 in self.via_page_url_regex:
                        for regex_2 in self.single_shop_regex:
                            if url not in crawled and (regex_1.search(url) or regex_2.search(url)):
                                yield scrapy.Request(url, callback=self.parse_js)
                else:
                    for regex in self.single_shop_regex:
                        if regex.search(url):
                            yield scrapy.Request(url, callback=self.parse_js)
        counter = 0
        for a in driver.find_elements_by_xpath('//*[@onclick]'):
            clickdriver = webdriver.PhantomJS()
            clickdriver.get(response.url)
            clickdriver.find_elements_by_xpath('//*[@onclick]')[counter].click()
            if len(clickdriver.window_handles)>1:
                clickdriver.switch_to_window(clickdriver.window_handles[1])
                yield scrapy.Request(url=clickdriver.current_url, callback=self.parse_js)
                clickdriver.close()
                clickdriver.switch_to_window(clickdriver.window_handles[0])
                clickdriver.close()
            else:
                yield scrapy.Request(url=clickdriver.current_url, callback=self.parse_js)
                clickdriver.close()
            counter+=1
        driver.close()
