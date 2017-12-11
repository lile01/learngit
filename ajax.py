# _*_ encoding:utf-8 _*_
import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import json
import re
import os
from hashlib import md5
from multiprocessing import Pool

def get_page_first(offset,keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 3
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/56.0'}
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求异常！')
        return None

def parse_page_first(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            # print(item)
            yield item.get('article_url')

def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_page_detail(htmlchird):
    soup = BeautifulSoup(htmlchird, 'lxml')
    #print(soup.prettify())
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile("gallery:(.*?),\n", re.S)
    result = re.search(images_pattern, htmlchird)
    # print(result.group(1))
    if result: # 判断是否成功
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            # print(sub_images)
            #for item in sub_images:
                 #print(item.get('url'))
            images_url = [item.get('url') for item in sub_images]
            for image in images_url:
                download_image(image)


def download_image(url):
    print('正在下载', url)
    try:
        response = requests.get("http:" + url)
        if response.status_code == 200:
            # print(response.content)
            save_image(response.content, url)
        return None
    except RequestException:
        print("请求图片出错！")
        return None

def save_image(content, url):
    file_path = '{0}/{1}.{2}'.format('./jiepai', url[30:], 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_page_first(offset, '街拍')
    #parse_page_first(html)
    #print(html)
    for url in parse_page_first(html):
        htmlchird = get_page_detail(url)
        parse_page_detail(htmlchird)


if __name__ == "__main__":
    po = Pool()
    for i in range(0, 5):
        po.apply_async(main, (i*20,))
    po.close()
    po.join()
    # main()
