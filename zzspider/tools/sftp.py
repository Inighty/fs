#!/usr/bin/env python3
# coding: utf-8
import os

import paramiko

from zzspider import settings
from zzspider.tools.singleton_type import Singleton


class Sftp(metaclass=Singleton):
    # 构造函数
    def __init__(self, host=settings.SFTP_HOST, user=settings.SFTP_USER,
                 pwd=settings.SFTP_PASSWD):
        self.t = paramiko.Transport(host, 22)
        self.t.banner_timeout = 10
        self.t.connect(username=user, password=pwd)
        self.sftp = paramiko.SFTPClient.from_transport(self.t)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname=host, port=22, username=user, password=pwd)

    def close(self):
        self.t.close()
        self.ssh.close()

    def upload(self, local_path, remote_path):
        self.sftp.put(local_path, remote_path)
        return True

    def upload_to_dir(self, local_path, remote_path):
        self.ssh.exec_command("mkdir -p " + remote_path)
        head, tail = os.path.split(local_path)
        self.sftp.put(local_path, remote_path + '/' + tail)
        return True

    def upload_batch_to_dir(self, local_paths, remote_path):
        self.ssh.exec_command("mkdir -p " + remote_path)
        for path in local_paths:
            head, tail = os.path.split(path)
            self.sftp.put(path, remote_path + '/' + tail)
        return True
