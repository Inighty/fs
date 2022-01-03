import os

import PIL
from PIL import Image


def img_to_progressive(path):
    if not path.split('.')[-1:][0] in ['png', 'jpg', 'jpeg']:
        return
    if os.path.isdir(path):
        return
    img = Image.open(path)
    destination = path.split('.')[:-1][0] + '_destination.' + path.split('.')[-1:][0]
    try:
        print(path.split('/')[-1:][0], '开始转换图片')
        img.save(destination, "PNG", quality=80, optimize=True, progressive=True)  # 转换就是直接另存为
        print(path.split('/')[-1:][0], '转换完毕')
    except IOError:
        PIL.ImageFile.MAXBLOCK = img.size[0] * img.size[1]
        img.save(destination, "PNG", quality=80, optimize=True, progressive=True)
        print(path.split('/')[-1:][0], '转换完毕')
    print('开始重命名文件')
    os.remove(path)
    os.rename(destination, path)
