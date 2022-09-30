import json
import os
import platform
import random

import requests
from PIL import Image as pilImage
from pygifsicle import optimize
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


plat = platform.system().lower()


def img_to_progressive(path):
    if not os.path.exists(path):
        return path
    if os.path.isdir(path):
        return path
    ext = path.split('.')[-1:][0]
    if ext == 'svg':
        pic = svg2rlg(path)
        final_path = path.replace('.svg', '.png')
        renderPM.drawToFile(pic, final_path)
        os.remove(path)
        path = final_path
    if ext == 'tif':
        im = pilImage.open(path)
        out = im.convert("RGB")
        final_path = path.replace('.tif', '.jpeg')
        out.save(final_path, "JPEG", quality=90)
        os.remove(path)
        path = final_path

    ext = path.split('.')[-1:][0]
    if ext == 'gif':
        compress_gif(path)
        return path
    if ext not in ['png', 'jpg', 'jpeg']:
        return path

    if os.path.getsize(path) > (5 * 1024 * 1024):
        shrink_image(path)
    return path


def compress_gif(filename):
    destination = os.path.splitext(filename)[0] + '_destination' + os.path.splitext(filename)[1]
    optimize(source=filename, destination=destination,
             options=['-O3', '--lossy=90', '--no-extensions', '--no-comments'], colors=256)
    os.remove(filename)
    os.rename(destination, filename)
    # with Image(filename=filename) as img:
    #     img.fuzz = img.quantum_range * 0.05
    #     img.optimize_layers()
    #     img.save(filename=destination)
    #     print("des: " + destination)
    # exit(0)


def list_images(path):
    images = None
    try:
        if path:
            os.chdir(path)
        full_path = os.getcwd()
        files = os.listdir(full_path)
        images = []
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png'):
                images.append(os.path.join(full_path, file))
    except:
        pass
    return images


def local_compress_image(path):
    destination = os.path.splitext(path)[0] + '_destination' + os.path.splitext(path)[1]
    img_size = int(os.path.getsize(path))
    if os.path.isfile(path) and os.path.splitext(path)[1] == '.png':
        cmd = 'pngquant --force --skip-if-larger --output {} --quality 50-80 --verbose {}'.format(destination, path)
        rt = os.system(cmd)
        if rt == 0:
            print(path.split('/')[-1:][0], '转换完毕')
            new_img_size = int(os.path.getsize(destination))
            if new_img_size >= img_size:
                os.remove(destination)
                print('图片变大了，不做处理：' + str(img_size) + '--->' + str(new_img_size))
            else:
                print('开始重命名文件')
                os.remove(path)
                os.rename(destination, path)
                print('图片大小：' + str(img_size) + '--->' + str(new_img_size))
                return

    if img_size < 500000:
        return
    img = pilImage.open(path)

    if img.mode == "CMYK":
        img = img.convert('RGB')
    new_width = 600
    if img.size[0] > new_width:
        new_height = int(new_width * img.size[1] * 1.0 / img.size[0])
        img = img.resize((new_width, new_height))
    print(path.split('/')[-1:][0], '开始转换图片')
    img.save(destination, "PNG", quality=60, optimize=True, progressive=True)
    print(path.split('/')[-1:][0], '转换完毕')
    new_img_size = int(os.path.getsize(destination))
    if new_img_size >= img_size:
        os.remove(destination)
        print('图片变大了，不做处理：' + str(img_size) + '--->' + str(new_img_size))
    else:
        print('开始重命名文件')
        os.remove(path)
        os.rename(destination, path)
        print('图片大小：' + str(img_size) + '--->' + str(new_img_size))
        return


def shrink_image(file_path):
    print(file_path)
    try:
        result = shrink(file_path)
        if result:
            output_path = os.path.splitext(file_path)[0] + '_destination' + os.path.splitext(file_path)[1]
            url = result['output']['url']
            response = requests.get(url)
            with open(output_path, 'wb') as file:
                file.write(response.content)
            os.remove(file_path)
            os.rename(output_path, file_path)
            print('%s %d=>%d(%f)' % (
                result['input']['type'],
                result['input']['size'],
                result['output']['size'],
                result['output']['ratio']
            ))
        else:
            print('压缩失败')
    except:
        local_compress_image(file_path)


def shrink(file_path):
    url = 'https://tinypng.com/web/shrink'
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'X-Forwarded-For': get_random_ip()
    }
    result = None
    try:
        file = open(file_path, 'rb')
        response = requests.post(url, headers=headers, data=file)
        result = json.loads(response.text)
    except:
        if file:
            file.close()
    if result and result['input'] and result['output']:
        return result
    else:
        return None


def get_random_ip():
    ip = []
    for i in range(4):
        ip.append(str(random.randint(0 if i in (2, 3) else 1, 254)))
    return '.'.join(ip)


if __name__ == '__main__':
    compress_gif("E:/Desktop/123.gif")
