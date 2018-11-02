import random
import time

import requests
from pyquery import PyQuery as pq
from requests import RequestException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

url = 'http://www.biquge.com.tw/'
base_address = '/home/chief/python/novels/ebooks'
headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
IPs = [
    {'HTTPS': 'https://115.237.16.200:8118'},
    {'HTTPS': 'https://42.49.119.10:8118'},
    {'HTTPS': 'http://60.174.74.40:8118'}
]

def ChromeDriverNOBrowser():
   chrome_options = Options()
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--disable-gpu')
   driverChrome = webdriver.Chrome(chrome_options=chrome_options)
   return driverChrome

class EBook:
    '''
    根据输入的书名，爬取小说
    '''


    def get_book_result(self, name):
        '''
        根据书名，搜索小说，
        :param name: 书名
        :return: book_name, book_url author, last_update, about_book, 章节各个目录及url
        '''

        #driver = webdriver.PhantomJS()
        driver = ChromeDriverNOBrowser()
        driver.get(url)
        search = driver.find_element_by_name('searchkey')
        search.clear()
        search.send_keys(name)
        search.send_keys(Keys.RETURN)

        #   切换到最新窗口
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        book_url = driver.current_url
        if 'modules' in book_url:
            book_names = driver.find_elements_by_css_selector('#nr > td.odd > a')
            book_urls = driver.find_elements_by_css_selector('#nr > td.odd > a[href]')
            new_chapters = driver.find_elements_by_css_selector('#nr > td.even > a')
            new_chapter_urls = driver.find_elements_by_css_selector('#nr > td.even> a[href]')
            authors = driver.find_elements_by_css_selector('#nr > td:nth-child(3)')
            fonts = driver.find_elements_by_css_selector('#nr > td:nth-child(4)')
            times = driver.find_elements_by_css_selector('#nr > td:nth-child(5)')
            status = driver.find_elements_by_css_selector('#nr > td:nth-child(6)')
            datas = []
            for book_name, book_url, new_chapter, new_chapter_url, author, font, time, statu in zip(book_names, book_urls, new_chapters, new_chapter_urls, authors, fonts, times, status):
                datas.append({'book_name': book_name.text, 'book_url': book_url.get_attribute('href'), 'new_chapter': new_chapter.text,
                             'new_chapter_url': new_chapter_url.get_attribute('href'),
                             'author': author.text, 'font': font.text, 'time': time.text, 'statu': statu.text})
            print(datas)
            return datas
        else:
            datas = []
            div = driver.find_element_by_css_selector('#maininfo')
            book_name = div.find_element_by_css_selector('#info > h1').text
            author = div.find_element_by_css_selector('#info > p:nth-child(2)').text.split('：')[1]
            last_update = div.find_element_by_css_selector('#info > p:nth-child(4)').text.split('：')[1]
            new_chapter = div.find_element_by_css_selector('#info > p:nth-child(5) > a[href]')
            # info > p:nth-child(3) > a:nth-child(1)
            # info > p:nth-child(5) > a
            new_chapter_name = new_chapter.text
            print(new_chapter_name)
            new_chapter_url = new_chapter.get_attribute('href')
            print(new_chapter_url)

            data = {'book_name': book_name, 'book_url': book_url, 'new_chapter': new_chapter_name,
                    'new_chapter_url': new_chapter_url,'author': author, 'font': '未知', 'time': last_update,
                                  'statu': '未知'}
            datas.append(data)
            return datas



    def get_chapters_url(self, url):
        '''
        获取书籍的所有url
        :param url:
        :return:
        '''

        ip = random.choice(IPs)

        try:
            response = requests.get(url, headers=headers, proxies=ip)
            response.encoding = 'GBK'
            html = response.text
            doc = pq(html)
            about_book = doc.find('#intro > p').text()
            image = 'http://www.biquge.com.tw' + doc.find('#fmimg > img[src]').attr['src']
            print(image)
            chapters = doc.find('#list > dl > dd > a[href]').items()
            datas = []
            i = 1
            for chapter in chapters:
                datas.append({'chapter_number': i, 'chapter_name': chapter.text(), 'chapter_url': 'http://www.biquge.com.tw' + chapter.attr('href')})
                i = i + 1
            return datas, about_book, image


        except RequestException as e:
            print(e.args)
            self.get_chapters_url(url)
        except Exception as e:
            print(e.args)
            self.get_chapters_url(url)


    def get_chapter_content(self, url):
        '''
        下载一章节内容
        '''


        ip = random.choice(IPs)

        try:

            response = requests.get(url, headers=headers, proxies=ip)
            response.encoding = 'GBK'
            html = response.text
            doc = pq(html)
            #chapter_name = doc('#wrapper > div.content_read > div > div.bookname > h1').text()
            content = doc('#content').text().replace('\n\n', '</p><p>')
            #html = '''<div><h3>{name}</h3><p>{content}'''.format(name=chapter_name, content=content)
            return content

        except RequestException as e:
            print(e.args)
            self.get_chapter_content(url)
        except Exception as e:
            print(e.args)
            self.get_chapter_content(url)


if __name__ == '__main__':
    #name = input('请输入书名: ')
    ebook = EBook()
    ebook.get_book_result('三寸人间')
    #ebook.get_chapters_url('http://www.biquge.com.tw/1_1686/')





