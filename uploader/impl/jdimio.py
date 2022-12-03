import base64
import json
import random
import re

import requests

from uploader.impl import AbstractUploader


class Uploader(AbstractUploader):
    def upload(self) -> str:
        with open(self.path, 'rb') as f:
            base64Img = base64.b64encode(f.read()).decode()
        r = requests.post(
            'https://imio.jd.com/uploadfile/file/post.do',
            data={
                's': base64Img,
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
                'X-Forwarded-For': '.'.join(str(random.randint(0, 255)) for x in range(4)),
                'cookie': 'shshshfpa=129debfe-ca49-6414-3a49-c0e59c80cffd-1661995538; shshshfpb=ir0ye8EzETtxNcLwHvyTaSQ; pinId=JM4MIRsy4vB6pkKvm8_uK0p5mukvpktY; ipLoc-djd=22-1930-50948-57092; unpl=JF8EAO5nNSttWEIGBUgFSEUYH19XW1VdTh5QbTQDA1laQ1UMTgUbE0N7XlVdXhRLFx9sZhRXXFNJUA4eAysSFXtdVV9dDE4UAGlmNWQGDR8dQAcCHhsYQ1RVXV4NQxYCaG8AVV1eV1UZGzIYEiBKbVRZWghDHwdrZQJdVVxLVAQfCxMbGUpdZF9tCEMTM29mBFVeWEtUAxwFGCIQSlxUWVsOSh4EAWIEVVxaSlQEHAt1EBFKXlJWWQlDFDNvbgVWVVlKVAIYMhoiEXsLOl5cCUoWAmpnBlYQWExTBRMKHxYSTFRcWl0IShMKZ24MVV1oSmQG; __jdv=122270672|kong|t_1001542270_1001677086_4000301068_3002795092|tuiguang|18c1b6bf9e3249d48b3b7f53908d610b|1668947743969; cluster=1_file-dd-gray.jd.com_file-dd-gray.jd.com; PCSYCityID=CN_510000_510100_0; shshshfp=f4d24904f86238c3df6ef9cafe871f4d; TrackID=1PpskT9EqmjP_OmZycanHfYNVf4uoXWNnJLGggh8Upy3jFjhHSivHYxMWP_H4mlaT4kL4PZb2HazDaORgDVM69AQgLN95IvFTi_NBzo_dfWk; thor=6A9894E3FF4BC8C7827A49FF293F124973E892B6680AF8D95B36F9F493D7CB71A52A1595D91A0AC1834B27A6D655FA9827E51936DFF3E0F449E32EA34700356A972C1530AE7C45A3979E43147203F4788E846F134EFC4396A54601AED8F66AB460A685D53D42907AEBB31D44F67FDEC59632C767C71396BD578B21C45BE3E45EB6CD70EE06B42FF62499D3A1A6CA55EB099FAF9B83CDD4405EC4F3336623B049; pin=338692009-44026883; unick=Inighty; ceshi3.com=201; _tp=P8DuNgRE1iqbsKzKnB0YdaIS6XkSqJCj7nkQvSUdMgg%3D; _pst=338692009-44026883; shshshsID=41fbe7572e43699abc7da1b26cfd4f84_2_1670072168056; wlfstk_smdl=myornpnr60auzt9qij3otxrovg640l5m; 3AB9D23F7A4B3C9B=G3MXLK2PNM7H74I5RNVQH2NH7PHL4CSK2KBLLM5H2FUP4PHNGDZUVPYZEO6AQFL3VLUG5NRX3LN7IRNKIZA36VP7ME; __jda=76161171.16619955368951105898801.1661995536.1668947744.1670072154.23; __jdb=76161171.7.16619955368951105898801|23.1670072154; __jdc=76161171; __jdu=1670072183980387438542; visitkey=49061211228817287'
            }
        )
        r.raise_for_status()
        return json.loads(re.search(r'<body>(.+)</body>', r.text).group(1))['path'].replace('http://', 'https://')
