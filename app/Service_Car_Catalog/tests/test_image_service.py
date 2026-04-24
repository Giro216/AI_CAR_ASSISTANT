import asyncio
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.service.imageService import SerperImageService


class FakeResponse:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return self._payload


class FakeSession:
    def __init__(self, response_factory):
        self._response_factory = response_factory

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def post(self, url, json, headers):
        return self._response_factory(url, json, headers)


def run(coro):
    return asyncio.run(coro)


def test_get_image_url_returns_none_without_credentials(monkeypatch):
    service = SerperImageService(api_key=None)

    def should_not_be_called(*args, **kwargs):
        raise AssertionError("ClientSession should not be called when credentials are missing")

    monkeypatch.setattr("app.service.imageService.aiohttp.ClientSession", should_not_be_called)

    result = run(service.get_image("Toyota Camry car"))

    assert result is None


def test_get_image_returns_image_response_on_success(monkeypatch):
    service = SerperImageService(api_key="key")

    def response_factory(url, payload, headers):
        assert url == "https://google.serper.dev/images"
        assert payload["q"] == "Toyota Camry car"
        assert headers["X-API-KEY"] == "key"
        return FakeResponse(
            200,
            {
                "images": [
                    {
                        "title": "Toyota Camry",
                        "imageUrl": "https://img.example/camry.jpg",
                        "imageWidth": 1200,
                        "imageHeight": 800,
                        "source": "Example",
                        "domain": "img.example",
                        "link": "https://img.example/camry-page",
                        "position": 1,
                    }
                ]
            },
        )

    monkeypatch.setattr(
        "app.service.imageService.aiohttp.ClientSession",
        lambda timeout: FakeSession(response_factory),
    )

    result = run(service.get_image("Toyota Camry car"))

    assert result is not None
    assert result.imageUrl == "https://img.example/camry.jpg"
    assert result.title == "Toyota Camry"


def test_get_image_url_returns_none_on_empty_items(monkeypatch):
    service = SerperImageService(api_key="key")

    def response_factory(url, payload, headers):
        return FakeResponse(200, {"images": []})

    monkeypatch.setattr(
        "app.service.imageService.aiohttp.ClientSession",
        lambda timeout: FakeSession(response_factory),
    )

    result = run(service.get_image("BMW X5 car"))

    assert result is None


def test_get_image_url_returns_none_on_http_error(monkeypatch):
    service = SerperImageService(api_key="key")

    def response_factory(url, payload, headers):
        return FakeResponse(500, {})

    monkeypatch.setattr(
        "app.service.imageService.aiohttp.ClientSession",
        lambda timeout: FakeSession(response_factory),
    )

    result = run(service.get_image("Kia Rio car"))

    assert result is None


def test_get_image_url_uses_cache_for_repeated_query(monkeypatch):
    service = SerperImageService(api_key="key")
    calls = {"count": 0}

    def response_factory(url, payload, headers):
        calls["count"] += 1
        return FakeResponse(200, {"images": [{"title": "Toyota RAV4", "imageUrl": "https://img.example/rav4.jpg"}]})

    monkeypatch.setattr(
        "app.service.imageService.aiohttp.ClientSession",
        lambda timeout: FakeSession(response_factory),
    )

    first = run(service.get_image("Toyota RAV4 car"))
    second = run(service.get_image("Toyota RAV4 car"))

    assert first is not None
    assert second is not None
    assert first.imageUrl == "https://img.example/rav4.jpg"
    assert second.imageUrl == "https://img.example/rav4.jpg"
    assert calls["count"] == 1


@pytest.mark.skipif(
    os.getenv("RUN_REAL_SERPER_TESTS") != "1" or not os.getenv("SERPER_API_KEY"),
    reason="Для реального запроса задать RUN_REAL_SERPER_TESTS=1 и SERPER_API_KEY",
)
def test_get_image_real_request_returns_non_empty_link():
    service = SerperImageService(api_key=os.getenv("SERPER_API_KEY"))

    image = run(service.get_image("Toyota Camry 2020"))

    assert image is not None
    assert isinstance(image.imageUrl, str)
    assert image.imageUrl.strip() != ""
    assert image.imageUrl.startswith("http")
