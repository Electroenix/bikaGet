import argparse
import os.path
import shutil
import configparser
import bika
from metaconfig import ComicInfo, update_metadate


# 使文件和目录名称合法化,不能对路径名使用,会把\去掉
def make_filename_valid(path):
    path = path.replace('/', '')
    path = path.replace('\\', '')
    path = path.replace(':', '')
    path = path.replace('*', '')
    path = path.replace('?', '')
    path = path.replace('<', '')
    path = path.replace('>', '')
    path = path.replace('"', '')
    path = path.replace('|', '')
    path = path.rstrip()
    return path


config = configparser.ConfigParser()  # 全局配置项
config.read("config.ini", encoding="utf-8")


if __name__ == "__main__":

    paser = argparse.ArgumentParser()
    paser.add_argument("comic_view_url", help="哔咔漫画详情页的url")
    paser.add_argument("-c", "--chapter", help="指定要下载的章节列表，数字，以‘,’分隔，如‘1,2,3,5,7’，未指定该项默认下载全部章节")

    args = paser.parse_args()
    comic_view_url = args.comic_view_url
    chapter_id_list = []
    if args.chapter:
        chapter_id_list = args.chapter.split(",")

    # 请求bika数据
    comic_info = ComicInfo()
    bika.request_comic_info(comic_view_url, comic_info, chapter_id_list)
    print("系列:%s" % comic_info.series_title)
    print("作者:%s" % comic_info.author)
    print("标签:%s" % comic_info.genres)
    print("获取到%d个章节" % len(comic_info.chapter_list))

    '''
    目录结构
        comic 在脚本目录下创建用于保存下载的漫画
        |- series_title 漫画系列名
            |- series_title_001.epub 保存的epub格式的漫画
            |- series_title_002.epub
            |- series_title_xxx.epub
            |- chapter_title 以章节名命名的文件夹，临时存放下载的图片，转换成epub格式后就会被删除
                |- 00001.jpg
                |- 00002.jpg
                |- xxxxx.jpg
    '''
    save_dir = "comic"
    comic_dir = save_dir + "/" + make_filename_valid(comic_info.series_title)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    if not os.path.exists(comic_dir):
        os.mkdir(comic_dir)

    chapter_index = 1
    for c in comic_info.chapter_list:
        chapter_title = make_filename_valid(c.title)
        chapter_dir = comic_dir + "/" + chapter_title

        if not os.path.exists(chapter_dir):
            os.mkdir(chapter_dir)

        # 开始下载章节图片
        print("\r\n正在下载第%d章" % c.id)
        bika.download_images(c.id, chapter_dir)
        print("\r\n下载完成！")

        epub_name = make_filename_valid(comic_info.series_title) + "_%03d.epub" % chapter_index
        epub_path = comic_dir + "/" + epub_name

        if config["option"]["trans_epub"] == "true":
            print("\r\nkcc-c2e开始转换epub...")

            # 调用kcc-c2e转换图片为epub格式
            kcc_c2e_path = config["path"]["kcc-c2e"]
            cmd = '"%s" "%s" -t "%s" -f KFX -o "%s" -m --forcecolor -n' % (kcc_c2e_path, chapter_dir, c.title, epub_path)
            os.system(f'"{cmd}"')

            # 更新epub中的metadata
            update_metadate(epub_path, epub_path, c.metadata)
            print("\r\n转换完成, 漫画保存在%s" % epub_path)

        # 删除图片文件夹
        if config["option"]["del_image"] == "true" and config["path"]["kcc-c2e"]:
            shutil.rmtree(chapter_dir)

        chapter_index = chapter_index + 1

