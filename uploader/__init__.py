from importlib import import_module

from uploader.impl import AbstractUploader


class Uploader:
    @staticmethod
    def get(server: str, path: str) -> AbstractUploader:
        return import_module(f'uploader.impl.{server}').Uploader(path)
