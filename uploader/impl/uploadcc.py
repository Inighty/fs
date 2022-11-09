from uploader.impl import AbstractUploader


class Uploader(AbstractUploader):
    @property
    def request_url(self) -> str:
        return 'https://upload.cc/image_upload'

    @property
    def file_key(self) -> str:
        return 'uploaded_file[]'

    @property
    def parsed(self) -> str:
        return f'https://upload.cc/{self.request.json()["success_image"][0]["url"]}'
