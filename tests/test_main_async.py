import pathlib
import sys

import aiohttp
import pytest
from aiohttp import web

# Ensure the src directory is on the path for imports
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from main import fetch_example_async


async def _start_test_server(handler, port):
    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", port)
    await site.start()
    return runner


@pytest.mark.asyncio
async def test_fetch_example_async_success(unused_tcp_port):
    async def handler(request):
        return web.Response(text="Example Domain")

    runner = await _start_test_server(handler, unused_tcp_port)
    url = f"http://localhost:{unused_tcp_port}"
    try:
        assert await fetch_example_async(url, limit=7) == "Example"
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_fetch_example_async_http_error(unused_tcp_port):
    async def handler(request):
        return web.Response(status=404)

    runner = await _start_test_server(handler, unused_tcp_port)
    url = f"http://localhost:{unused_tcp_port}"
    try:
        assert await fetch_example_async(url) == "Error fetching data"
    finally:
        await runner.cleanup()


@pytest.mark.asyncio
async def test_fetch_example_async_exception(monkeypatch):
    def raise_error(self, url, **kwargs):  # type: ignore[override]
        raise aiohttp.ClientError("boom")

    monkeypatch.setattr(aiohttp.ClientSession, "get", raise_error)
    result = await fetch_example_async("https://example.com")
    assert result.startswith("Error fetching data:")


@pytest.mark.asyncio
async def test_fetch_example_async_invalid_limit():
    with pytest.raises(ValueError):
        await fetch_example_async(limit=0)


@pytest.mark.asyncio
async def test_fetch_example_async_env_vars(unused_tcp_port, monkeypatch):
    async def handler(request):
        return web.Response(text="Example Domain")

    runner = await _start_test_server(handler, unused_tcp_port)
    url = f"http://localhost:{unused_tcp_port}"
    monkeypatch.setenv("FETCH_URL", url)
    monkeypatch.setenv("FETCH_LIMIT", "7")
    try:
        assert await fetch_example_async() == "Example"
    finally:
        await runner.cleanup()

