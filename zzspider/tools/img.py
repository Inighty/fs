import os

from PIL import Image


def img_to_progressive(path):
    if os.path.isdir(path):
        return
    ext = path.split('.')[-1:][0]
    if ext == 'gif':
        compress_gif(path)
        return
    if ext not in ['png', 'jpg', 'jpeg']:
        return
    destination = os.path.splitext(path)[0] + '_destination.' + os.path.splitext(path)[1]
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
    img = Image.open(path)

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


def compress_gif(path):
    gif = Image.open(path)  # 读取文件
    indexnum = getIndex(gif)
    mergeGif(indexnum)
    removeImg(indexnum)


# 提取gif逐帧保存并返回帧数
def getIndex(img):
    index = 1
    # 图片为gif时获取帧数index并逐帧压缩
    if img.is_animated == True:
        try:
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGB')  # 逐帧转换成RGB
                frame.save("index%d.jpg" % index)  # 保存每一帧
                pressImg('index%d.jpg' % index)  # 调用压缩图片函数逐帧压缩
                index = index + 1
            return index
        except Exception as e:
            print('Error:' + e)
    # 非gif时帧数index为1
    else:
        return index


# 压缩图片
def pressImg(ImgName):
    img = Image.open(ImgName)
    img.convert('RGB')
    if max(img.size[0], img.size[1]) > 128:  # 若帧图宽高有一项大于128则压缩
        img.thumbnail((128, 128))
    img.save('press-' + ImgName, quality=60)  # 此处quality为保存图片质量 取值范围由1(最差)-95(最好)
    return 'OK'


# 合并gif
def mergeGif(indexnum):
    images = []
    for i in range(1, indexnum):
        images.append(imageio.imread('press-index%d.jpg' % i))
    imageio.mimsave(r'C:\Users\Evaron\Desktop\QRTEST.gif', images)


# 删除中间产生的图片
def removeImg(indexnum):
    for i in range(1, indexnum):
        af = 'press-index' + str(i) + '.jpg'
        bf = 'index' + str(i) + '.jpg'
        if os.path.exists(af):
            os.remove(af)
        if os.path.exists(bf):
            os.remove(bf)
