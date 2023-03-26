import os.path
import pickle
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains


class WebDriver:
    def __init__(self, path="resources/geckodriver-linux64", invisible=True):
        self.path = path
        self.driver = self.init_web_driver(invisible=invisible)
        # self.load_cookies()

    def init_web_driver(self, invisible=False):
        profile = webdriver.FirefoxProfile()
        options = Options()
        options.add_argument("user-data-dir=resource/cookie.pkl")
        options.headless = invisible
        profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        # profile.set_preference("pdfjs.disabled", True)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf, application/octet-stream, application/x-winzip, application/x-pdf, application/x-gzip")
        profile.set_preference("plugin.scan.Acrobat", "99.0")
        profile.set_preference("plugin.scan.plid.all", False)
        web_driver = webdriver.Firefox(options=options, firefox_profile=profile, executable_path=self.path)
        return web_driver

    def save_cookies(self, path="resource/cookie.pkl"):
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(path, "wb+"))

    def load_cookies(self, path="resource/cookie.pkl"):
        if os.path.isfile(path):
            with open(path, "rb") as cookies_files:
                cookies = pickle.load(cookies_files)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.refresh()
        else:
            # raise FileNotFoundError("Can not found file " + path)
            print("Can not found file " + path)

    def restart_driver(self):
        if self.driver is not None:
            self.driver.close()
        self.driver = self.init_web_driver(False)

    def refresh(self):
        self.driver.refresh()

    def close(self):
        self.driver.close()

    def goto(self, url):
        self.driver.get(url)

    def scroll(self, agent):
        """

        :param agent: int: scroll down when agent > 0; up when agent < 0;
                      selenium-element: scroll into view the element
        :return:
        """
        if isinstance(agent, int):
            self.driver.execute_script(f"window.scrollTo(0,{agent})")
        else:
            self.driver.execute_script("arguments[0].scrollIntoView();", agent)

    def hover(self, element):
        """
        Hover over a element
        :param element:
        :return:
        """
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()


if __name__ == "__main__":
    w = WebDriver(path="resource/geckodriver")
    uri = "http://youtube.com"
    w.goto(uri)
    # time.sleep(20)
    w.load_cookies("resource/cookie_fb.pkl")
    time.sleep(18)
    # w.save_cookies()
    w.close()
