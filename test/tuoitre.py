import json
import urllib.request
from bs4 import BeautifulSoup
from tqdm import tqdm

menu = {
    3: "Thời sự",
    2: "Thế giới",
    6: "Pháp luật",
    11: "Kinh doanh",
    200029: "Công nghệ",
    659: "Xe",
    100: "Du lịch",
    7: "Nhịp sống trẻ",
    200017: "Văn hóa",
    10: "Giải trí",
    1209: "Thể thao",
    13: "Giáo dục",
    661: "Khoa học",
    12: "Sức khỏe"
}


def checker(id_, page):
    sourceHTML = urllib.request.urlopen(f"https://tuoitre.vn/timeline/{id_}/trang-{page}.htm").read()
    soup = BeautifulSoup(sourceHTML, 'html.parser')
    if len(soup.select("li h3.title-news a")) > 0:
        return True
    return False


def find_limit_page(id_, max_value):
    low = 1
    high = max_value
    mid = (high + low) // 2
    while low < high:
        mid = (high + low) // 2
        if checker(id_, mid):
            low = mid + 1
        else:
            high = mid - 1

    return mid


def find_id():
    try:
        with open("../resource/categories.json", "r") as fr:
            idjson = json.loads(fr.read())
            m = max([int(i) for i in idjson.keys()])
    except:
        idjson = {}
        m = 0

    for i in tqdm(range(m, 700), position=0):
        if checker(i, 1):
            idjson[int(i)] = find_limit_page(i, 2000)
        if i % 300 == 0:
            with open("../resource/categories.json", "w+") as fw:
                fw.write(json.dumps(idjson))
    print(json.dumps(idjson))
    with open("../resource/categories.json", "w+") as fw:
        fw.write(json.dumps(idjson))


if __name__ == "__main__":
    from downloader.tuoitre import TuoitreDownload
    from Redis import REDIS_CUSTOM
    d = TuoitreDownload(2, REDIS_CUSTOM)
    aa = d.get_info("https://tuoitre.vn//phat-hien-ho-chon-105-nguoi-mexico-dieu-tra-quan-chuc-dia-phuong-998890.htm")
    print(aa)
    # find_id()
    # print(find_limit_page(2, 100))
    # print(checker(2, 99))
