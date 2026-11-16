import scrapy

import time, random
from urllib.parse import urlencode
from userdetail.sign import xdynosaur
from userdetail.utils.ua_lib import UserAgentService
class UserDetailSpider(scrapy.Spider):
    name = "user"

    def __init__(self, name = None, **kwargs):
        super().__init__(name, **kwargs)

        self.base_url = "https://www.tiktok.com/api/user/detail/?"
        self.base_unique_id = "jetjet_10a2"
        self.ua_service = UserAgentService()
        # self.ms_token = "AA-WE3BapeOZjweCZWdihAA9YOce9aXzIBvxo61eea6wNuGdIiLSen5rab0zOuvq4wc_vBWFAvAsqtl0VcfC2iq-8p7KR9WqZkr4QiIOHm_pBEzOmuO6OlS9LyQN5L2BMIUS4bcig3aPlMoIRYPkoq68TO0eDKnB1k_-wj8="
        self.ms_token ="9cZntTyK5Q1RIsXx1SlSf9ypx9cg23fZ4wnwrXx1abMS3HykilKIkYJxQEoxl1rFchHV4GvoZI6D4KN_vW0F4xLpXC4x-sn9uhaUv1sf71gHdcBcN-FydUXtdYifUpG2neFli9ouViK2kjlPwrt-8t7hkUTOCIKrNKmWrKKYRw=="
    def start_requests(self):

        target = self.ua_service.target_random()
        print("Browser= ", target)

        ua = self.ua_service.get_user_agent(target)

        qs = self.parse_param(unique_id=self.base_unique_id, target=target)

        dyno = self.sign_dyno(param=qs, ua=ua)

        headers_mod = {
            'Accept': '*/*',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://www.tiktok.com',
            'Referer': f'https://www.tiktok.com/@{self.base_unique_id}',
        }

        fn_url = self.base_url + qs + "&X-Dynosaur=" + dyno + "&msToken=" + self.ms_token
        
        yield scrapy.Request(
            url="https://httpbin.org/headers",
            method="GET",
            headers=headers_mod,
            callback=self.parse,
            errback=self.errback,
            meta={
                "curl_cffi_options": {
                    "impersonate": f"{target}",
                }
            },
            dont_filter=True,
        )

    def parse(self, response):
        print("data raw:", response.text)

    def errback(self, failure):
        self.logger.error(repr(failure))

    def sign_dyno(self, param, ua):
        dyno = xdynosaur.encrypt(qs=param, body="", ua=ua)
        return dyno
    
    def parse_param(self, unique_id, target):
        
        metadata = self.ua_service.get_browser_metadata(target)

        now = int(time.time())

        device_id = (
            7472955720000000000
            + random.randint(10000000000, 100000000000)
        )

        params = {
            "WebIdLastTime": now,
            "abTestVersion": "[object Object]",
            "aid": 1988,
            "appType": "t",
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": metadata["browser_name"],
            "browser_online": "true",
            "browser_platform": metadata["browser_platform"],
            "browser_version": metadata["browser_version"],
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "data_collection_enabled": "true",
            "device_id": device_id,
            "device_platform": metadata["device_platform"],
            "focus_state": "true",
            "from_page": "user",
            "history_len": 3,
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": "en",
            "needAudienceControl": "true",
            "odinId": "7666392169548366866",
            "os": metadata["os"],
            "priority_region": "",
            "referer": "",
            "region": "VN",
            "root_referer": "",
            "screen_height": 1200,
            "screen_width": 1920,
            "secUid": "",
            "tz_name": "Asia/Ho_Chi_Minh",
            "uniqueId": unique_id,
            "user_is_login": "false",
            "webcast_language": "en",
        }

        return urlencode(params)