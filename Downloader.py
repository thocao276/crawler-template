import json
import multiprocessing
import time
from datetime import datetime

import requests

from Driver import WebDriver
from Redis import REDIS_CUSTOM


class Downloader:
    def __init__(self, path, redis_agent: REDIS_CUSTOM, selector_dict: dict):
        self.web_driver = WebDriver(path=path, invisible=True)
        self.redis_agent = redis_agent
        self.selector = selector_dict

    def login(self, user="None", password="Zxcvbnm,./"):
        self.web_driver.driver.get("https://www.facebook.com/")
        self.web_driver.driver.find_element_by_css_selector(self.selector['login']['user']).send_keys(user)
        self.web_driver.driver.find_element_by_css_selector(self.selector['login']['password']).send_keys(password)
        self.web_driver.driver.find_element_by_css_selector(self.selector['login']['login_btn']).click()

    def get(self, url):
        self.web_driver.driver.get(url)

    def save_image(self, url, name):
        self.get(url)
        image = self.web_driver.driver.find_element_by_css_selector(self.selector['image']['source']).get_attribute(
            "src")
        with open(name, "wb+") as f:
            data = requests.get(image).content
            f.write(data)

    def worker(self, process_name):
        time.sleep(0.5)
        while 1:
            if self.redis_agent.list_len("download") == 0:
                print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}  -  No tasks in the queue {process_name}')
                time.sleep(10)
                continue
            fb_id = self.redis_agent.brpop("download")
            print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")} [SAVED] Process: {process_name}; {fb_id}.jpg"')
            self.save_image(f"https://www.facebook.com/photo/?fbid={fb_id}", f"{fb_id}.jpg")


def run(number_process, selector, path="resource/geckodriver", redis_agent=REDIS_CUSTOM):
    processes = list()
    engine_list = list()
    for process_name in range(number_process):
        engine_list.append(Downloader(path=path, redis_agent=redis_agent, selector_dict=selector))
        downloader_engine = engine_list[process_name]
        p = multiprocessing.Process(target=downloader_engine.worker, args=(process_name,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()


if __name__ == "__main__":
    with open("resource/selector_path.json", "r") as fr:
        selector_ = json.loads(fr.read())
    run(number_process=5, selector=selector_, path="resource/geckodriver", redis_agent=REDIS_CUSTOM)
