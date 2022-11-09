from uploader.impl import AbstractUploader


class Uploader(AbstractUploader):
    @property
    def request_url(self) -> str:
        return 'https://zhidao.baidu.com/submit/ajax'

    @property
    def file_key(self) -> str:
        return 'image'

    @property
    def form(self) -> dict:
        return {
            'cm': 100672,
        }

    @property
    def parsed(self) -> str:
        return self.request.json()['url'].split('?')[0]
