import os

from uploader.impl import AbstractUploader


class Uploader(AbstractUploader):
    @property
    def request_url(self) -> str:
        return 'https://kfupload.alibaba.com/mupload'

    @property
    def file_key(self) -> str:
        return 'file'

    @property
    def form(self) -> dict:
        ext = os.path.splitext(self.path)[1]
        if ext.lower() not in {'.jpg', '.jpeg', '.gif', '.png'}:
            ext = '.jpg'
        return {
            'scene': 'productImageRule',
            'name': f'image{ext}'
        }

    @property
    def parsed(self) -> str:
        return self.request.json()['url']

    @property
    def headers(self) -> dict:
        return {
            'User-Agent': 'iAliexpress/8.33.0 (iPhone; iOS 12.1.2; Scale/2.00)',
        }
