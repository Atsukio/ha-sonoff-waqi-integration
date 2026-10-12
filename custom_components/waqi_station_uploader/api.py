"""Minimal async client for the WAQI data upload API."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp

from .const import TOKEN_CHECK_URL, UPLOAD_URL

REQUEST_TIMEOUT = 20


class WaqiError(Exception):
    """Generic WAQI error."""


class WaqiAuthError(WaqiError):
    """Token was rejected."""


class WaqiConnectionError(WaqiError):
    """WAQI could not be reached."""


async def _request(
    session: aiohttp.ClientSession, method: str, url: str, **kwargs: Any
) -> dict[str, Any]:
    try:
        async with asyncio.timeout(REQUEST_TIMEOUT):
            async with session.request(method, url, **kwargs) as resp:
                text = await resp.text()
                status = resp.status
    except (aiohttp.ClientError, TimeoutError) as err:
        raise WaqiConnectionError(f"Cannot reach WAQI: {err!r}") from err

    if status != 200:
        raise WaqiError(f"HTTP {status}: {text[:200]}")
    try:
        data = json.loads(text)
    except ValueError as err:
        raise WaqiError(f"Invalid JSON response: {text[:200]}") from err
    if not isinstance(data, dict):
        raise WaqiError(f"Unexpected response: {text[:200]}")
    return data


def _error_message(data: dict[str, Any]) -> str:
    return str(data.get("data") or data.get("message") or data)


async def async_validate_token(session: aiohttp.ClientSession, token: str) -> None:
    """Check the token against the WAQI JSON API. Raises on failure."""
    data = await _request(session, "GET", TOKEN_CHECK_URL, params={"token": token})
    if data.get("status") == "ok":
        return
    message = _error_message(data)
    if "invalid key" in message.lower() or "token" in message.lower():
        raise WaqiAuthError(message)
    raise WaqiError(message)


async def async_upload(
    session: aiohttp.ClientSession, payload: dict[str, Any]
) -> dict[str, Any]:
    """POST a payload to the WAQI sensor upload endpoint."""
    data = await _request(session, "POST", UPLOAD_URL, json=payload)
    if data.get("status") != "ok":
        message = _error_message(data)
        if "invalid key" in message.lower():
            raise WaqiAuthError(message)
        raise WaqiError(message)
    return data
