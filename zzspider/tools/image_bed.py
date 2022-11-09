import logging
import os

from uploader import Uploader
from zzspider.config import ConfigUtil
from zzspider.tools.img import img_to_progressive

logger = logging.getLogger(__name__)


def upload(file: str):
    print("localfile:" + file)
    file = img_to_progressive(file)
    if os.path.getsize(file) > (10 * 1024 * 1024):
        logger.error("the file is too large: " + file)
        return None
    url = None
    try:
        url = Uploader.get(ConfigUtil.config['upload']['server'], file).upload()
    except Exception as ex:
        result = f'\033[91m{type(ex).__name__}\033[39m \033[93m{ex}\033[39m'
        logger.error("upload file error:" + result, ex)
    return url


if __name__ == '__main__':
    print(upload("E:/Desktop/111.jpg"))
