"""The Redis client.

Gate 0 needs Redis to exist, to be reachable and to round-trip a value. It deliberately builds no
queue, no rate limiter and no cache-aside helper: those are shaped by the component that needs them,
and inventing an abstraction now would mean Gate 2 either works around it or replaces it.

The client is created once and closed at shutdown. ``redis.asyncio`` pools connections internally,
so a module-level client would keep sockets open past the lifetime of the application — which is
exactly what makes a test suite hang on teardown.
"""

from __future__ import annotations

from redis.asyncio import Redis

from iacode_api.config import Settings


def create_client(settings: Settings) -> Redis:
    """Build the client. It connects lazily, so a down Redis does not prevent startup."""
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=settings.readiness_timeout_seconds,
        socket_timeout=settings.readiness_timeout_seconds,
        health_check_interval=30,
    )


async def ping(client: Redis) -> None:
    """Prove Redis answers. Raises when it does not."""
    await client.ping()


async def close(client: Redis) -> None:
    """Release every pooled connection, including the ones the pool is holding idle."""
    await client.aclose()
