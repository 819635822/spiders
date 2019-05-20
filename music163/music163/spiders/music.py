# -*- coding: UTF-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import json
import sys

import scrapy
from scrapy import Request, FormRequest
from scrapy.settings.default_settings import DEFAULT_REQUEST_HEADERS

reload(sys)
sys.setdefaultencoding("utf-8")


class MusicSpider(scrapy.Spider):
    name = "music"
    allowed_domains = ["163.com"]
    base_url = 'https://music.163.com'
    ids = ['1001']
    # ids = ['1001', '1002', '1003', '2001', '2002', '2003', '6001', '6002', '6003', '7001', '7002', '7003', '4001',
    #        '4002', '4003']
    # initials = [i for i in range(65, 90)] + [0]
    initials = [i for i in range(65, 66)] + [0]

    def parse(self, response):

        pass

    def start_requests(self):
        for id in self.ids:
            for initial in self.initials:
                url = '{url}/discover/artist/cat?id={id}&initial={initial}'.format(url=self.base_url, id=id,
                                                                                   initial=initial)
                yield Request(url, callback=self.parse_index)

    def parse_index(self, response):
        # //*[@id="m-artist-box"]/li/@href
        artists = response.xpath('//*[@id="m-artist-box"]/li/a[1]/@href').extract()
        for artist in artists:
            artist_url = self.base_url + '/artist' + '/album?' + artist[8:]
            yield Request(artist_url, callback=self.parse_artist)

    def parse_artist(self, response):
        albues = response.xpath('//*[@id="m-song-module"]/li/div/a[1]/@href').extract()
        for albue in albues:
            album_url = self.base_url + albue
            yield Request(album_url, callback=self.parse_album)

    def parse_album(self, response):
        musics = response.xpath('//*[@id="song-list-pre-cache"]/ul/li/a/@href').extract()
        for music in musics:
            music_id = music[9:]
            music_url = self.base_url + music
            yield Request(music_url, meta={'id': music_id}, callback=self.parse_music)

    def parse_music(self, response):
        music_id = response.meta['id']
        name = response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/div[1]/div/em/text()').extract()
        album = response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[2]/a/text()').extract()
        # todo 可能为多个
        artist = response.xpath('/html/body/div[3]/div[1]/div/div/div[1]/div[1]/div[2]/p[1]/span/@title').extract()

        data = {
            'csrf_token': '',
            'params': 'Ak2s0LoP1GRJYqE3XxJUZVYK9uPEXSTttmAS+8uVLnYRoUt/Xgqdrt/13nr6OYhi75QSTlQ9FcZaWElIwE+oz9qXAu87t2DHj6Auu+2yBJDr+arG+irBbjIvKJGfjgBac+kSm2ePwf4rfuHSKVgQu1cYMdqFVnB+ojBsWopHcexbvLylDIMPulPljAWK6MR8',
            'encSecKey': '8c85d1b6f53bfebaf5258d171f3526c06980cbcaf490d759eac82145ee27198297c152dd95e7ea0f08cfb7281588cdab305946e01b9d84f0b49700f9c2eb6eeced8624b16ce378bccd24341b1b5ad3d84ebd707dbbd18a4f01c2a007cd47de32f28ca395c9715afa134ed9ee321caa7f28ec82b94307d75144f6b5b134a9ce1a'
        }
        DEFAULT_REQUEST_HEADERS['Referer'] = self.base_url + '/playlist?id=' + str(music_id)
        music_comment = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_' + str(music_id)

        yield FormRequest(music_comment, meta={'id': music_id, 'music': name, 'artist': artist, 'album': album},
                          callback=self.parse_comment, formdata=data)

    def parse_comment(self, response):
        id = response.meta['id']
        music = response.meta['music']
        artist = response.meta['artist']
        album = response.meta['album']
        result = json.loads(response.text)
        comments = []
        if 'hotComments' in result.keys():
            for comment in result.get('hotComments'):
                hotcomment_author = comment['user']['nickname']
                hotcomment = comment['content']
                hotcomment_like = comment['likedCount']
                # 这里我们将评论的作者头像也保存，如果大家喜欢这个项目，我后面可以做个web端的展现
                hotcomment_avatar = comment['user']['avatarUrl']
                data = {
                    'nickname': hotcomment_author,
                    'content': hotcomment,
                    'likedcount': hotcomment_like,
                    'avatarurl': hotcomment_avatar
                }
                comments.append(data)

        item = MusicItem()
        # 由于eval方法不稳定，具体的可以自己搜索，我们过滤一下错误
        for field in item.fields:
            try:
                item[field] = eval(field)
            except:
                print('Field is not defined', field)
        print item
        yield item
