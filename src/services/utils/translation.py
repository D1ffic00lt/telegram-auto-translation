import random
import requests
import httpx

from typing import Any
from string import ascii_lowercase, digits
from copy import deepcopy
from abc import ABC, abstractmethod

from .exceptions import APIException

__all__ = ("TranslationInterface", "MymemoryAPI", "LibreTranslateAPI")


class TranslationInterface(ABC):
    @abstractmethod
    def translate(
        self,
        text: str,
        *,
        source_language: str = "auto",
        translation_language: str = "english",
    ) -> str: ...

    @abstractmethod
    async def translate_async(
        self,
        text: str,
        *,
        source_language: str = "auto",
        translation_language: str = "english",
    ) -> str: ...


class MymemoryAPI(TranslationInterface):
    def __init__(
        self,
        link: str = "https://api.mymemory.translated.net/get",
        email_domains: list[str] = None,
    ):
        self.link = link
        if email_domains is None:
            self.email_domains = ["@gmail.com", "@icloud.com", "@yandex.ru", "@edu.hse.ru"]
        else:
            self.email_domains = email_domains

    def translate(
        self,
        text: str,
        *,
        source_language: str = "ru",
        translation_language: str = "en",
    ) -> str:
        response: requests.Response = requests.get(
            self.link,
            params={"q": text, "langpair": f"{source_language}|{translation_language}", "de": self._generate_email()},
        )
        return self._process_response(response).replace("\\n", "\n")

    async def translate_async(
        self,
        text: str,
        *,
        source_language: str = "ru",
        translation_language: str = "en",
    ) -> str:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(
                self.link,
                params={
                    "q": text,
                    "langpair": f"{source_language}|{translation_language}",
                    "de": self._generate_email(),
                },
            )
        return self._process_response(response)

    def _generate_email(self) -> str:
        return "".join(random.choices(ascii_lowercase + digits, k=15)) + random.choice(self.email_domains)

    @staticmethod
    def _process_response(response: requests.Response | httpx.Response):
        if response.status_code // 100 != 2:
            raise APIException(f"mymemory api raised an exception ({response.status_code})")

        response: dict[str, Any] = response.json()

        if response["responseDetails"] != "":
            raise APIException("responseDetails is not empty")

        if response["quotaFinished"]:
            raise APIException("quota is left")
        # print(response["responseData"]["translatedText"])
        return response["responseData"]["translatedText"]


class LibreTranslateAPI(TranslationInterface):
    def __init__(self, link: str = "http://libretranslate:5001/translate"):
        self.link = link

    def translate(
        self,
        text: str,
        *,
        source_language: str = "ru",
        translation_language: str = "en",
    ) -> str:
        response: requests.Response = requests.post(
            self.link,
            json={
                "q": text,
                "source": source_language,
                "target": translation_language,
                "format": "text",
                "alternatives": 0,
            },
        )
        return self._process_response(response)

    async def translate_async(
        self,
        text: str,
        *,
        source_language: str = "ru",
        translation_language: str = "en",
    ) -> str:
        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.post(
                self.link,
                json={
                    "q": text,
                    "source": source_language,
                    "target": translation_language,
                    "format": "text",
                    "alternatives": 0,
                },
            )
        return self._process_response(response)

    @staticmethod
    def _process_response(response: requests.Response | httpx.Response) -> str:
        if response.status_code // 100 != 2:
            raise APIException(f"LibreTranslate api raised an exception ({response.status_code})")

        response: dict[str, Any] = response.json()

        if "translatedText" not in response:
            raise APIException("No response")

        return response["translatedText"]
