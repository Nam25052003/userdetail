import random

from enum import Enum
from dataclasses import dataclass


class BrowserTarget(str, Enum):
    CHROME = "chrome"
    EDGE = "edge"
    SAFARI = "safari"
    # SAFARI_IOS = "safari_ios"
    # CHROME_ANDROID = "chrome_android"
    FIREFOX = "firefox"


@dataclass(frozen=True)
class BrowserFingerprint:
    target: str
    browser: str
    version: str
    os: str
    os_version: str


class UserAgentService:

    # Tương ứng với REAL_TARGET_MAP trong curl_cffi.
    TARGET_MAP = {
        "chrome": "chrome152",
        "edge": "edge101",
        "safari": "safari270",
        "safari_ios": "safari270_ios",
        "chrome_android": "chrome131_android",
        "firefox": "firefox155",
    }

    # Metadata lấy theo NATIVE_IMPERSONATE_TARGETS.
    FINGERPRINTS = {
        "chrome152": BrowserFingerprint(
            target="chrome152",
            browser="Chrome",
            version="152",
            os="Windows",
            os_version="10",
        ),
        "edge101": BrowserFingerprint(
            target="edge101",
            browser="Edge",
            version="101",
            os="Windows",
            os_version="10",
        ),
        "safari270": BrowserFingerprint(
            target="safari270",
            browser="Safari",
            version="27.0",
            os="macOS",
            os_version="27.0",
        ),
        "safari270_ios": BrowserFingerprint(
            target="safari270_ios",
            browser="Safari",
            version="27.0",
            os="iOS",
            os_version="27.0",
        ),
        "chrome131_android": BrowserFingerprint(
            target="chrome131_android",
            browser="Chrome",
            version="131",
            os="Android",
            os_version="14",
        ),
        "firefox155": BrowserFingerprint(
            target="firefox155",
            browser="Firefox",
            version="155.0",
            os="Windows",
            os_version="10",
        ),
    }

    @classmethod
    def target_random(cls) -> str:
        """
        Random browser family.

        Returns:
            chrome | edge | safari | safari_ios |
            chrome_android | firefox
        """
        return random.choice(list(BrowserTarget)).value

    @classmethod
    def resolve_target(cls, target: str) -> str:
        """
        Resolve browser alias to native target.
        """
        target = target.lower()

        resolved = cls.TARGET_MAP.get(target, target)

        if resolved not in cls.FINGERPRINTS:
            raise ValueError(f"Unsupported browser target: {target}")

        return resolved

    @classmethod
    def get_user_agent(cls, target: str) -> str:
        """
        Generate User-Agent from browser target.
        """
        resolved = cls.resolve_target(target)
        fingerprint = cls.FINGERPRINTS[resolved]

        browser = fingerprint.browser.lower()
        version = fingerprint.version
        os_name = fingerprint.os

        if browser == "chrome":
            return cls._chrome_ua(fingerprint)

        if browser == "edge":
            return cls._edge_ua(fingerprint)

        if browser == "safari":
            return cls._safari_ua(fingerprint)

        if browser == "firefox":
            return cls._firefox_ua(fingerprint)

        raise ValueError(f"Unsupported browser: {browser}")

    @staticmethod
    def _chrome_ua(fp: BrowserFingerprint) -> str:

        if fp.os == "Windows":
            platform = "Windows NT 10.0; Win64; x64"

        elif fp.os == "macOS":
            platform = "Macintosh; Intel Mac OS X 10_15_7"

        elif fp.os == "Android":
            platform = (
                f"Linux; Android {fp.os_version}; Pixel 7"
            )

            return (
                f"Mozilla/5.0 ({platform}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{fp.version}.0.0.0 "
                f"Mobile Safari/537.36"
            )

        else:
            raise ValueError(f"Unsupported OS: {fp.os}")

        return (
            f"Mozilla/5.0 ({platform}) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{fp.version}.0.0.0 Safari/537.36"
        )

    @staticmethod
    def _edge_ua(fp: BrowserFingerprint) -> str:

        return (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            f"AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{fp.version}.0.0.0 Safari/537.36 "
            f"Edg/{fp.version}.0.0.0"
        )

    @staticmethod
    def _safari_ua(fp: BrowserFingerprint) -> str:

        if fp.os == "iOS":
            return (
                f"Mozilla/5.0 (iPhone; CPU iPhone OS "
                f"{fp.os_version.replace('.', '_')} like Mac OS X) "
                f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
                f"Version/{fp.version} Mobile/15E148 Safari/604.1"
            )

        return (
            f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            f"AppleWebKit/605.1.15 (KHTML, like Gecko) "
            f"Version/{fp.version} Safari/605.1.15"
        )

    @staticmethod
    def _firefox_ua(fp: BrowserFingerprint) -> str:

        if fp.os == "Windows":
            platform = "Windows NT 10.0; Win64; x64"

        elif fp.os == "macOS":
            platform = "Macintosh; Intel Mac OS X 10.15"

        else:
            raise ValueError(f"Unsupported OS: {fp.os}")

        return (
            f"Mozilla/5.0 ({platform}; rv:{fp.version}) "
            f"Gecko/20100101 Firefox/{fp.version}"
        )
    
    @classmethod
    def get_browser_metadata(cls, target: str) -> dict:
        resolved = cls.resolve_target(target)
        fp = cls.FINGERPRINTS[resolved]

        # navigator.platform
        platform_map = {
            "Windows": "Win32",
            "macOS": "MacIntel",
            "Android": "Linux armv8l",
            "iOS": "iPhone",
        }

        # OS trong TikTok query parameters
        os_map = {
            "Windows": "windows",
            "macOS": "mac",
            "Android": "android",
            "iOS": "ios",
        }

        # Platform token trong Mozilla/5.0 (...)
        browser_version_map = {
            "Windows": "5.0 (Windows NT 10.0; Win64; x64)",
            "macOS": "5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Android": f"5.0 (Linux; Android {fp.os_version}; Pixel 7)",
            "iOS": (
                f"5.0 (iPhone; CPU iPhone OS "
                f"{fp.os_version.replace('.', '_')} like Mac OS X)"
            ),
        }

        return {
            "browser_name": "Mozilla",
            "browser_version": browser_version_map[fp.os],
            "browser_platform": (
                "Linux x86_64"
                if fp.os == "Linux"
                else platform_map[fp.os]
            ),
            "os": os_map[fp.os],
            "device_platform": (
                "web_mobile" if fp.os in ("Android", "iOS") else "web_pc"
            ),
        }