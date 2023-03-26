from tqdm import tqdm
from Redis import REDIS_CUSTOM, RedisCustom
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup


class TuoitreScrapper:

    def __init__(self, redis_agent: RedisCustom):
        self.redis_agent = redis_agent

    def get_source(self, url_):
        sourceHTML = urllib.request.urlopen(url_).read()
        return BeautifulSoup(sourceHTML, 'html.parser')

    def get_post_current_page(self, post):
        sourceHTML = urllib.request.urlopen(post).read()
        soup = BeautifulSoup(sourceHTML, 'html.parser')
        for url_ in soup.select("li h3.title-news a"):
            url_ = urllib.parse.urljoin("http://tuoitre.vn", url_['href'])
            if not self.redis_agent.set_is_exist("visited", url_):
                print(url_)
                self.redis_agent.set_add("visited", url_)
                self.redis_agent.list_add_left("crawl", url_)


if __name__ == "__main__":
    Scrapper = TuoitreScrapper(REDIS_CUSTOM)
    for page in range(1500, 2501):
        print(page)
        url = f"https://tuoitre.vn/timeline/0/trang-{page}.htm"
        Scrapper.get_post_current_page(url)
