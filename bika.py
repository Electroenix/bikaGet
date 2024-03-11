import requests
import time
import hmac
from hashlib import sha256
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from metaconfig import ComicMetaData, ChapterInfo
from bikaget import config


# 用来存储从bika获取到的数据
class BikaComicInfo:
    title = ""
    author = ""
    genres = []
    description = ""
    chapter = []

    def __init__(self):
        self.title = ""
        self.author = ""
        self.genres = []
        self.description = ""
        self.chapter = []


bika_comic_info = BikaComicInfo()
headers_api = {
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "nonce": "",
    "app-uuid": "webUUID",
    "time": "",
    "sec-ch-ua-mobile": "?0",
    "authorization": "",
    "app-channel": "1",
    "app-platform": "android",
    "content-type": "application/json; charset=UTF-8",
    "accept": "application/vnd.picacomic.com.v1+json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "signature": "",
    "image-quality": "original",
    "sec-ch-ua-platform": "\"Windows\"",
    "origin": "https://manhuabika.com",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-encoding": "gzip, deflate, zstd",
    "accept-language": "zh-CN,zh-TW;q=0.9,zh;q=0.8,en-GB;q=0.7,en;q=0.6,zh-MO;q=0.5,zh-HK;q=0.4,ja-JP;q=0.3,ja;q=0.2",
}

headers_image = {
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-dest': 'image',
    'accept-encoding': 'gzip, deflate, zstd',
    'accept-language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-GB;q=0.7,en;q=0.6,zh-MO;q=0.5,zh-HK;q=0.4,ja-JP;q=0.3,ja;q=0.2'
}

host = "go2778.com"
base_url = "https://api." + host + "/"
applekillflag = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
appleversion = r"~d}$Q7$eIni=V)9\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"


def get_token():
    return config["http"]["token"]


def get_nonce():
    return config["http"]["nonce"]


def get_signature(url, ts, method):
    raw = url.replace(base_url, "") + ts + get_nonce() + method + applekillflag
    raw = raw.lower()
    hmac_object = hmac.new(appleversion.encode(), raw.encode(), digestmod=sha256)
    return hmac_object.hexdigest()


# 获取漫画详情页面的信息
def get_comic_view_info(cid):
    path_name = "comics/" + cid
    url = base_url + path_name
    headers_api["time"] = str(int(time.time()))
    headers_api["authorization"] = get_token()
    headers_api["nonce"] = get_nonce()
    headers_api["signature"] = get_signature(path_name, headers_api["time"], "GET")
    response = requests.request("GET", url, headers=headers_api)

    resp_json = response.json()
    comic_json = resp_json["data"]["comic"]

    bika_comic_info.title = comic_json["title"]
    bika_comic_info.author = comic_json["author"]
    bika_comic_info.genres = list(set(comic_json["categories"] + comic_json["tags"]))
    bika_comic_info.description = comic_json["description"]


# 获取漫画章节
def get_comic_chapter(cid, page_cnt=1):
    path_name = "comics/" + cid + "/eps?page=" + str(page_cnt)
    url = base_url + path_name

    headers_api["time"] = str(int(time.time()))
    headers_api["authorization"] = get_token()
    headers_api["nonce"] = get_nonce()
    headers_api["signature"] = get_signature(path_name, headers_api["time"], "GET")
    response = requests.request("GET", url, headers=headers_api)

    resp_json = response.json()
    bika_comic_info.chapter = bika_comic_info.chapter + resp_json["data"]["eps"]["docs"]
    page_max = int(resp_json["data"]["eps"]["pages"])

    if page_cnt < page_max:
        get_comic_chapter(cid, page_cnt + 1)
    else:
        # 获取完所有章节信息后，列表中order是降序的，将列表反转便于后续通过order查找元素，由于order从1开始，在列表前面补位一个和列表index对齐
        bika_comic_info.chapter.reverse()
        bika_comic_info.chapter.insert(0, "占位用的，使 chapter order 和列表 index 对齐，方便定位")


# 获取漫画章节图片
def get_comic_chapter_pages(cid, chapter_id, page_cnt=1):
    path_name = "comics/" + cid + "/order/" + str(chapter_id) + "/pages?page=" + str(page_cnt)
    url = base_url + path_name

    headers_api["time"] = str(int(time.time()))
    headers_api["authorization"] = get_token()
    headers_api["nonce"] = get_nonce()
    headers_api["signature"] = get_signature(path_name, headers_api["time"], "GET")
    response = requests.request("GET", url, headers=headers_api)

    resp_json = response.json()
    if "pages" in bika_comic_info.chapter[chapter_id]:
        bika_comic_info.chapter[chapter_id]["pages"] = bika_comic_info.chapter[chapter_id]["pages"] + \
                                                       resp_json["data"]["pages"]["docs"]
    else:
        bika_comic_info.chapter[chapter_id]["pages"] = resp_json["data"]["pages"]["docs"]

    pages_max = int(resp_json["data"]["pages"]["pages"])
    if page_cnt < pages_max:
        get_comic_chapter_pages(cid, chapter_id, page_cnt + 1)
    # else:
    #     print(bika_comic_info.chapter[chapter_id]["pages"])


def download(path, url, auto_retry=False):
    while True:
        try:
            response = requests.request("GET", url, headers=headers_image)
            with open(path, "wb") as f:
                f.write(response.content)
            break
        except Exception as result:
            if auto_retry:
                time.sleep(5)
                continue
            else:
                print('\r\nError! info: %s' % result)
                retry = input('下载失败，是否重新下载(y/n)')
                if retry == 'y':
                    continue
                else:
                    return -1


# 下载图片
def download_images(chapter_id, dir):
    image_index = 1
    threads_list = []
    pool = ThreadPoolExecutor(max_workers=10)
    for page in bika_comic_info.chapter[chapter_id]["pages"]:
        # 这里 page["path"] 不用处理也能get到图片，但是看浏览器里地址 “static/” 后面直接跟的文件名，就改成一样吧
        url = page["media"]["fileServer"] + "/static/" + page["media"]["path"].split("/")[-1]
        image_name = "%05d.jpg" % image_index
        image_path = dir + "/" + image_name

        # 加入下载线程
        threads_list.append(pool.submit(download, image_path, url, True))
        image_index = image_index + 1

    # 监测下载线程状态
    totle_cnt = len(threads_list)
    finish_cnt = 0
    for thread in as_completed(threads_list):
        finish_cnt = finish_cnt + 1
        print("\r%03d/%03d" % (finish_cnt, len(threads_list)), end="")


def request_comic_info(view_url, comic_info, chapter_id_list):
    view_url_parse = urlparse(view_url)
    cid = parse_qs(view_url_parse.query)["cid"][0]
    comic_info.view_url = view_url
    comic_info.cid = cid

    # 获取详情页信息
    get_comic_view_info(cid)
    # 获取全部章节信息
    get_comic_chapter(cid)

    comic_info.series_title = bika_comic_info.title
    comic_info.author = bika_comic_info.author
    comic_info.genres = bika_comic_info.genres

    # 若未指定章节，则默认下载全部章节
    if not chapter_id_list:
        chapter_id_list = range(1, len(bika_comic_info.chapter))

    for chapter_id in chapter_id_list:
        # 获取章节图片信息
        get_comic_chapter_pages(cid, int(chapter_id))

        chapter_info = ChapterInfo()
        chapter_info.title = bika_comic_info.chapter[int(chapter_id)]["title"]
        chapter_info.id = int(chapter_id)

        chapter_info.metadata.title = bika_comic_info.chapter[int(chapter_id)]["title"]
        chapter_info.metadata.creator = bika_comic_info.author
        chapter_info.metadata.subjects = bika_comic_info.genres
        if "英語 ENG" in bika_comic_info.genres:
            chapter_info.metadata.language = "en"
        elif "生肉" in bika_comic_info.genres:
            chapter_info.metadata.language = "ja"
        else:
            chapter_info.metadata.language = "zh"
        chapter_info.metadata.description = bika_comic_info.description

        comic_info.chapter_list.append(chapter_info)

    return 0
