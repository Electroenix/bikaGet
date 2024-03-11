from ebooklib import epub
import argparse


# comic元数据，以EPUB文件中元数据的标签命名
class ComicMetaData:
    title = ""
    creator = ""
    publisher = ""
    date = ""
    description = ""
    language = ""
    subjects = []

    def __init__(self):
        self.title = ""
        self.title = ""
        self.creator = ""
        self.publisher = ""
        self.date = ""
        self.description = ""
        self.language = ""
        self.subjects = []


class ChapterInfo:
    title = ""
    id = 0
    metadata = ComicMetaData()

    def __init__(self):
        self.title = ""
        self.id = 0
        self.metadata = ComicMetaData()

    
class ComicInfo:
    view_url = ""
    cid = ""
    series_title = ""  # 系列名
    author = ""  # 作者
    genres = []  # 标签
    chapter_list = []  # 漫画列表，可能有多个章节，以列表形式存储


# 更新epub文件中的metadata
def update_metadate(epub_path, output_path, metadata):

    # 读取epub文件
    book = epub.read_epub(epub_path)

    # 更新metadata
    if metadata.title:
        book.set_unique_metadata("DC", "title", metadata.title)

    if metadata.creator:
        book.set_unique_metadata("DC", "creator", metadata.creator)

    if metadata.description:
        book.set_unique_metadata("DC", "description", metadata.description)

    if metadata.language:
        book.set_unique_metadata("DC", "language", metadata.language)

    if metadata.subjects:
        book.set_unique_metadata("DC", "subject", metadata.subjects[0])
        for s in metadata.subjects[1:]:
            book.add_metadata("DC", "subject", s)

    # 保存epub文件
    epub.write_epub(output_path, book)


if __name__ == "__main__":
    paser = argparse.ArgumentParser()
    paser.add_argument("file", help="epub file path")
    paser.add_argument("-o", "--output", help="output file path")
    paser.add_argument("-t", "--title", help="comic title")
    paser.add_argument("-a", "--author", help="comic author")
    paser.add_argument("-d", "--describe", help="comic describe")
    paser.add_argument("-l", "--language", help="comic language")
    paser.add_argument("-s", "--subjects", help="comic subject/tags, split with \",\"")

    args = paser.parse_args()

    comic_meta = ComicMetaData()
    comic_meta.title = args.title
    comic_meta.creator = args.author
    comic_meta.description = args.describe
    comic_meta.language = args.language
    comic_meta.subjects = args.subjects.split(",")
    output_file = args.output
    file_path = args.file

    if not output_file:
        output_file = "test.epub"

    print("input file: %s" % file_path)
    print("output file: %s" % output_file)
    print("title: %s" % comic_meta.title)
    print("author: %s" % comic_meta.creator)
    print("description: %s" % comic_meta.description)
    print("language: %s" % comic_meta.language)
    print("subjects: ", end="")
    for s in comic_meta.subjects:
        print("[%s], " % s, end="")
    print()

    update_metadate(file_path, output_file, comic_meta)
