import json
import os
import random
import re
import time

import requests
from pyquery import PyQuery as pq
from requests import RequestException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from novel.novelSpider import SaveEpub

url = 'http://www.biquge.com.tw/'
base_address = '/home/chief/python/novels/ebooks'

def make_file(base_address):
    '''
    判断目录是否存在，不存在则创建
    :param base_address:
    :return:
    '''

    if not os.path.exists(base_address):
        os.mkdir(base_address)
    return


class EBook:
    '''
    根据输入的书名，爬取小说
    '''

    def __init__(self, name):
        '''

        :param name:  书名
        '''
        self.name = name
        self.driver = webdriver.Chrome()
        self.waitList = []
        self.failList = []



    def get_chapter_url(self):
        '''
        搜索小说，并找到所有章节url
        :return:
        '''

        time1 = time.time()
        self.driver.get(url)
        search = self.driver.find_element_by_name('searchkey')
        search.clear()
        search.send_keys(self.name)
        search.send_keys(Keys.RETURN)

        #   切换到最新窗口
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

        hrefs = self.driver.find_elements_by_css_selector('#list > dl > dd > a[href]')
        chapter_name = self.driver.find_elements_by_css_selector('#list > dl > dd > a')
        i = 1
        json_chapter = {}
        for href, chapter in zip(hrefs, chapter_name):
            #print(i)
            self.waitList.append({'chapter_number': i, 'chapter_url': href.get_attribute('href')})
            json_chapter[i] = chapter.text
            i += 1
        time2 = time.time()
        print(time2-time1)

        with open('chapter.json', 'w', encoding='utf-8') as f:
            json.dump(json_chapter, f, ensure_ascii=False)
        print('--------------')
        time3 = time.time()
        print(time3-time2)

        return self


    def get_chapter_content(self, chapter):
        '''
        下载一章节内容
        '''

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        IPs = [
            {'HTTPS': 'https://115.237.16.200:8118'},
            {'HTTPS': 'https://42.49.119.10:8118'},
            {'HTTPS': 'http://60.174.74.40:8118'}
        ]
        ip = random.choice(IPs)

        try:

            response = requests.get(chapter.get('chapter_url'), headers=headers, proxies=ip)
            response.encoding = 'GBK'
            html = response.text
            doc = pq(html)
            chapter_name = doc('#wrapper > div.content_read > div > div.bookname > h1').text()
            content = doc('#content').text().replace('\n\n', '</p><p>')
            html = '''<div><h3>{name}</h3><p>{content}'''.format(name=chapter_name, content=content)
            with open('/home/chief/python/novels/ebooks/{}.html'.format(chapter.get('chapter_number')), 'w') as f:
                f.write(html)

            if chapter in self.failList:
                self.failList.remove(chapter)


        except RequestException as e:
            print(e.args)
            self.failList.append(chapter)
        except Exception as e:
            print(e.args)
            self.failList.append(chapter)



    def get_all_chapters(self):
        '''
        下载所有章节
        :return:
        '''
        time1 = time.time()
        i = 1
        for chapter in self.waitList:
            print('正在爬取：', chapter.get('chapter_number'))
            self.get_chapter_content(chapter)


        if len(self.failList):
            for chapter in self.failList:
                print('正在爬取：', chapter.get('chapter_number'))
                self.get_chapter_content(chapter)
        time2 = time.time()
        print(time2-time1)


    def save_ebook(self):
        '''
        保存成一本
        :return:
        '''

        chapter_file = list(filter(lambda x: '.txt' in x, os.listdir('/home/chief/python/novels/ebooks')))
        chapter_file.sort(key=lambda x: int(re.match('\d+', x).group()))
        print(chapter_file)
        for chapter in chapter_file:
            with open('/home/chief/python/novels/ebooks/{}'.format(chapter), 'r') as f:
                content = f.read()
            if chapter is '1.txt':
                with open('/home/chief/python/novels/ebooks/{}.txt'.format(self.name), 'w') as f:
                    f.write(content + '\n'*10)
            else:
                with open('/home/chief/python/novels/ebooks/{}.txt'.format(self.name), 'a') as f:
                    f.write(content + '\n'*10)


if __name__ == '__main__':
    make_file(base_address)
    name = input('请输入书名: ')
    ebook = EBook(name)
    ebook.get_chapter_url()
    ebook.get_all_chapters()
    #ebook.save_ebook()
    epub = SaveEpub(title=name)
    epub.main()




