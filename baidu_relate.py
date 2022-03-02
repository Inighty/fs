import sys

from baiduspider import BaiduSpider

arg = sys.argv
if len(arg) > 1:
    start_word = arg[1]
    baiduspider = BaiduSpider()
    result_all = baiduspider.search_web(start_word, 1,
                                        ['news', 'video', 'baike', 'tieba', 'blog', 'gitee', 'calc', 'music'])
    for item in result_all.related:
        print(item)
    print("相关搜索数量：" + str(len(result_all.related)))
