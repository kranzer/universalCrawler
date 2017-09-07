# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawlersItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()

class CrawlersTestItem(scrapy.Item):
    engine_via_urls = scrapy.Field()
    engine_pagination_urls = scrapy.Field()
    engine_single_shop_urls = scrapy.Field()
