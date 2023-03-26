# import subprocess
#
# subprocess.call(["python3", "tuoitre.py"], cwd="../downloader")

import multiprocessing
from datetime import datetime
import re
import json

import requests

from Redis import RedisCustom, REDIS_CUSTOM
import time
import urllib.request
from bs4 import BeautifulSoup
import urllib.parse


def get_topic(url, source):
    topics = dict()
    tmp_penalty = False
    try:
        for t in source.select(".content-left  .bread-crumbs.fl li a"):
            if len(t.text) > 0:
                topics[urllib.parse.urljoin(url, t['href'])] = t.text
    except:
        # tmp_penalty = True
        pass
    return topics, tmp_penalty


def get_other_article(url, source):
    other = set()
    tmp_penalty = False
    try:
        [other.add(urllib.parse.urljoin(url, a['href'])) for a in
         source.find_all("a", {"href": re.compile(r'^/[a-z\-]{5,}\d{4,}\.htm')})]
    except:
        tmp_penalty = True
        pass
    return other, tmp_penalty


def get_keywords(url, source):
    keywords = dict()
    tmp_penalty = False
    try:
        for k in source.select(".tags-container ul.tags-wrapper li.tags-item a"):
            if len(k.text) > 0:
                keywords[urllib.parse.urljoin(url, k['href'])] = k.text
    except:
        tmp_penalty = True
    return keywords, tmp_penalty


def get_related_article(url, source):
    tmp_penalty = False
    related = set()
    try:
        for a in source.select("div.relate-container a"):
            tmp = urllib.parse.urljoin(url, a['href'])
            if tmp not in related:
                related.add(tmp)
    except:
        tmp_penalty = True
    return list(related), tmp_penalty


def get_author(source):
    tmp_penalty = False
    author = ""
    try:
        author = source.select_one(".author").text.strip()
    except:
        tmp_penalty = True
    return author, tmp_penalty


def get_content(source):
    tmp_penalty = False
    content = list()
    try:
        content = [p.text.strip() for p in source.select("div#main-detail-body > p")]
    except:
        tmp_penalty = True
    return content, tmp_penalty


def get_description(source):
    tmp_penalty = False
    description = ""
    try:
        description = source.select_one("h2.sapo").get_text()
    except:
        tmp_penalty = True
    return description, tmp_penalty


def get_public_time(source):
    tmp_penalty = False
    public_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    try:
        public_time = source.select_one(".date-time").text.strip()
    except:
        tmp_penalty = True
    return public_time, tmp_penalty


def get_title(source):
    title = ""
    tmp_penalty = False
    try:
        title = source.title.get_text()
    except:
        tmp_penalty = True
    return title, tmp_penalty


class TuoitreDownload:
    def __init__(self, topic_name, redis_agent: RedisCustom):
        self.redis_agent = redis_agent
        self.topic_name = topic_name

    def get_source(self, url):
        try:
            # sourceHTML = urllib.request.urlopen(url).read()
            sourceHTML = requests.get(url).content
            return BeautifulSoup(sourceHTML, 'html.parser')
        except:
            return None

    def add_other_url(self, urls):
        for url in urls:
            if not self.redis_agent.set_is_exist("visited", url):
                self.redis_agent.set_add("visited", url)
                self.redis_agent.list_add_left("crawl", url)

    def get_info(self, url, ischeckexist=True):
        source = self.get_source(url)
        penalty = 0

        if source is None:
            url = urllib.parse.urljoin("http://tuoitre.vn", urllib.parse.quote(url.split("/")[-1]))
            source = self.get_source(url)
            if source is None:
                print("None HTML source")
                return None, []

        if ischeckexist and self.redis_agent.hash_is_exist(self.topic_name, url):
            return None, []

        title, error = get_title(source)
        if error:
            penalty += 3

        public_time, tmp = get_public_time(source)
        if error:
            penalty += 1

        description, tmp = get_description(source)
        if error:
            penalty += 2

        content, tmp = get_content(source)
        if error:
            penalty += 3

        author, tmp = get_author(source)
        if error:
            penalty += 1

        related, tmp = get_related_article(url, source)
        keyword, tmp = get_keywords(url, source)
        topic, tmp = get_topic(url, source)
        other, tmp = get_other_article(url, source)

        if penalty > 7:
            return None, []

        article_info = {
            "url": url,
            "public_time": public_time,
            "crawled_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "title": title,
            "description": description,
            "content": content,
            "author": author,
            "related_post": related,
            "topic": list(topic.values()),
            "keywords": list(keyword.values())
        }

        self.save_info(keyword, topic, article_info)

        return article_info, other

    def save_info(self, keyword, topic, article_info):
        self.redis_agent.hash_add("keywords", keyword)
        self.redis_agent.hash_add("topic", topic)
        self.redis_agent.hash_add(self.topic_name, {article_info['url']: json.dumps(article_info)})

        with open(f"/home/thocao/Project/data/{article_info['url'].split('/')[-1]}.json", "w") as fw:
            fw.write(json.dumps(article_info))

    def download(self, pro_name):
        while self.redis_agent.list_len("crawl") > 0:
            # u = "http://tuoitre.vn" + self.redis_agent.dequeue("crawl")[1].decode()
            u = self.redis_agent.list_pop_right("crawl").decode()
            print(pro_name, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), u)
            try:
                output, other = self.get_info(u)
            except Exception as e:
                print("[Error] - ", e)
                self.redis_agent.list_add_left("crawl", u)
                continue
            if len(other) > 0:
                self.add_other_url(other)
            if self.redis_agent.list_len("crawl") < 5:
                print("Sleep 6s")
                time.sleep(6)
        print(pro_name, "BREAK THE LOOP at", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


def run(number_process, redis_agent=REDIS_CUSTOM):
    # https: // beckernick.github.io / faster - web - scraping - python /
    processes = list()
    for process_name in range(number_process):
        downloader_engine = TuoitreDownload("backup", redis_agent=redis_agent)
        p = multiprocessing.Process(target=downloader_engine.download, args=(process_name,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()


if __name__ == "__main__":
    run(14, REDIS_CUSTOM)
    # download = TuoitreDownload("backup", REDIS_CUSTOM)
    # u = "http://tuoitre.vn/​“muoi-tha”-chi-gay-ngua-khong-gay-benh-633586.htm"
    # output, _ = download.get_info(u, False)
    # print(output)
    # u = "http://tuoitre.vn/khoi-nhang-ngay-tet…-589118.htm"
    # while download.redis_agent.get_queue_len("crawl") > 1:
    #     u = "http://tuoitre.vn" + download.redis_agent.dequeue("crawl")[1].decode()
    #     output, other = download.get_info(u)
    #     if output is not None:
    #         download.add_other_url(other)
