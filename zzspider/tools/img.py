import os

from PIL import Image


def img_to_progressive(path):
    if not path.split('.')[-1:][0] in ['png', 'jpg', 'jpeg']:
        return
    if os.path.isdir(path):
        return
    destination = os.path.splitext(path)[0] + '_destination.' + os.path.splitext(path)[1]
    img_size = int(os.path.getsize(path))
    if os.path.isfile(path) and os.path.splitext(path)[1] == '.png':
        cmd = 'pngquant --force --skip-if-larger --output {} --quality 50-80 --verbose {}'.format(destination, path)
        rt = os.system(cmd)
        if rt == 0:
            print(path.split('/')[-1:][0], '转换完毕')
            print('开始重命名文件')
            os.remove(path)
            os.rename(destination, path)
            new_img_size = int(os.path.getsize(path))
            print('图片大小：' + str(img_size) + '--->' + str(new_img_size))
            return

    if img_size < 500000:
        return
    img = Image.open(path)

    if img.mode == "CMYK":
        img = img.convert('RGB')
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
