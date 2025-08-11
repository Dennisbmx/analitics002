import asyncio

import httpx


def test_health():
    async def _check():
        async with httpx.AsyncClient(base_url="http://localhost:8000") as c:
            r = await c.get("/")
            assert r.status_code == 200

    asyncio.run(_check())
