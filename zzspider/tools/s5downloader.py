import logging
from urllib.parse import urlsplit

from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler, ScrapyAgent
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from txsocksx.http import SOCKS5Agent

from zzspider.tools.proxyip import ProxyIp

logger = logging.getLogger(__name__)

# Ref https://txsocksx.readthedocs.io/en/latest/#txsocksx.http.SOCKS5Agent

import certifi, os

os.environ[
    "SSL_CERT_FILE"] = certifi.where()  # if not setted , you'll got an ERROR : certificate verify failed')] [<twisted.python.failure.Failure OpenSSL.SSL.Error: [('STORE routines', '', 'unregistered scheme')


class Socks5DownloadHandler(HTTP11DownloadHandler):

    def download_request(self, request, spider):
        """Return a deferred for the HTTP download"""
        settings = spider.settings
        agent = ScrapySocks5Agent(settings, contextFactory=self._contextFactory, pool=self._pool)
        return agent.download_request(request)


class ScrapySocks5Agent(ScrapyAgent):
    def __init__(self, settings, **kwargs):
        """
        init proxy pool
        """
        super(ScrapySocks5Agent, self).__init__(**kwargs)
        self.__proxy_file = settings['PROXY_FILE']

    def _get_agent(self, request, timeout):
        _, proxy_host, proxy_port = self.__random_choose_proxy()
        proxyEndpoint = TCP4ClientEndpoint(reactor, proxy_host, proxy_port)
        agent = SOCKS5Agent(reactor, proxyEndpoint=proxyEndpoint)
        return agent

    def __random_choose_proxy(self):
        """
        schema, host, port, user, pass
        :return:
        """
        line = ProxyIp().get()
        proxy_info = urlsplit(f"socks5://{line}")
        p = proxy_info.scheme, proxy_info.hostname, proxy_info.port
        logger.info("use proxy:" + proxy_info.hostname + ":" + str(proxy_info.port))
        return p
