# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MusicItem(scrapy.Item):
    # define the fields for your item here like:
    # 我们保存歌曲的id
    table_name = 'music'
    musicId = scrapy.Field()
    artist = scrapy.Field()
    album = scrapy.Field()
    musicName = scrapy.Field()
    comments = scrapy.Field()
