import json
import re
import time
import urllib.parse
from datetime import datetime

from selenium.webdriver.common.keys import Keys

from Driver import WebDriver
from Redis import REDIS_CUSTOM


def get_img_id(href):
    fbid = re.findall(r"(?<=fbid=)\d+", href)[0]
    return fbid


class Crawler:
    def __init__(self, path, invisible, redis_agent, selector_dict):
        self.web_driver = WebDriver(path, invisible=invisible)
        self.redis_agent = redis_agent
        self.selector = selector_dict

    def login(self):
        with open("resource/a.txt", "r") as account:
            user, password = account.read().split("\n")
        self.web_driver.driver.get("https://www.facebook.com/")
        self.web_driver.driver.find_element_by_css_selector(self.selector['login']['user']).send_keys(user)
        self.web_driver.driver.find_element_by_css_selector(self.selector['login']['password']).send_keys(password)
        self.web_driver.driver.find_element_by_css_selector(self.selector['login']['password']).send_keys(Keys.RETURN)

    def search_by_query(self, query):
        # self.web_driver.find_element_by_css_selector(self.selector['search']['button']).click()
        # bar_text = self.web_driver.find_element_by_css_selector(self.selector['search']['box'])
        # bar_text.send_keys(query)
        # bar_text.send_keys(Keys.RETURN)
        text_parsed = urllib.parse.quote(query)
        url = "https://www.facebook.com/search/photos/?q=" + text_parsed
        self.web_driver.driver.get(url)
        time.sleep(2)
        div_tag = self.web_driver.driver.find_elements_by_xpath(self.selector['elements']['see_all'])[1]
        div_tag.click()

    def get(self, url):
        self.web_driver.goto(url)

    def scroll(self):
        self.web_driver.driver.find_element_by_xpath(self.selector['elements']['results']).send_keys(Keys.PAGE_DOWN)
        time.sleep(1)


if __name__ == "__main__":
    # print(get_img_id("https://www.facebook.com/photo/?fbid=1362433357474489&set=g.1853667948249427"))
    with open("resource/selector_path.json", "r") as fr:
        selector = json.loads(fr.read())
    agent_crawl = Crawler(path="resource/geckodriver", invisible=False, redis_agent=REDIS_CUSTOM, selector_dict=selector)
    # agent_crawl.login()
    agent_crawl.get("https://www.facebook.com/groups/1853667948249427/media")
    # agent_crawl.web_driver.save_cookies("resource/cookies_fb.pkl")
    agent_crawl.web_driver.load_cookies("resource/cookies_fb.pkl")
    agent_crawl.get("https://www.facebook.com/groups/1853667948249427/media")
    time.sleep(13)
    agent_crawl.web_driver.close()
    # while 1:
    #     agent_crawl.scrap_image_url()
    #     time.sleep(0.5)
    #     agent_crawl.scroll()
    #     break
