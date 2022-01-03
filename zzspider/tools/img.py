import os

from PIL import Image


def img_to_progressive(path):
    if not path.split('.')[-1:][0] in ['png', 'jpg', 'jpeg']:
        return
    if os.path.isdir(path):
        return
    img_size = int(os.path.getsize(path))
    if img_size < 500000:
        return
    img = Image.open(path)
    destination = path.split('.')[:-1][0] + '_destination.' + path.split('.')[-1:][0]
    new_width = 600
    if img.size[0] > new_width:
        new_height = int(new_width * img.size[1] * 1.0 / img.size[0])
        img = img.resize((new_width, new_height))
    print(path.split('/')[-1:][0], '开始转换图片')
    img.save(destination, "PNG", quality=80, optimize=True, progressive=True)
    print(path.split('/')[-1:][0], '转换完毕')
    print('开始重命名文件')
    os.remove(path)
    os.rename(destination, path)
    new_img_size = int(os.path.getsize(path))
    print('图片大小：' + str(img_size) + '--->' + str(new_img_size))
