from uploader.impl import AbstractUploader


class Uploader(AbstractUploader):
    @property
    def request_url(self) -> str:
        return 'https://www.imooc.com/wenda/uploadimg'

    @property
    def file_key(self) -> str:
        return 'pic'

    @property
    def parsed(self) -> str:
        return self.request.json()['original'].replace('http://', 'https://')
