#!/usr/bin/env python3
"""Proves the pin check (scripts/check_pins.py) retries a 429, a 5xx or a timeout once, honoring
Retry-After up to its cap, and reports a 404 or a second failure at once. Offline: urlopen and sleep are
replaced.

Personal project, not for production, as is; not affiliated with the author's employer,
Liquidware or Microsoft.
"""
import io
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_pins  # noqa: E402

errors = []


def http(code, retry_after=None):
    headers = {"Retry-After": retry_after} if retry_after is not None else {}
    return urllib.error.HTTPError("https://example.invalid/", code, "x", headers, None)


for err, want in ((http(429, "12"), 12), (http(429, "600"), check_pins.RETRY_CAP), (http(503), 5),
                  (http(500, "soon"), 5), (urllib.error.HTTPError("u", 502, "x", None, None), 5),
                  (urllib.error.URLError("timed out"), 5), (TimeoutError(), 5), (http(404), None), (ValueError(), None)):
    got = check_pins.retry_after(err)
    if got != want:
        errors.append(f"retry_after({err!r}) is {got}, want {want}")


def run(answers):
    """fetch() against a scripted urlopen; returns (result or exception, calls, sleeps)."""
    calls, sleeps = [], []

    class Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(req, timeout):
        calls.append(req.full_url)
        answer = answers[len(calls) - 1]
        if isinstance(answer, BaseException):
            raise answer
        return Response(answer.encode())

    real = check_pins.urllib.request.urlopen, check_pins.time.sleep
    check_pins.urllib.request.urlopen, check_pins.time.sleep = urlopen, sleeps.append
    try:
        result = check_pins.fetch("https://example.invalid/page")
    except Exception as e:  # noqa: BLE001
        result = e
    finally:
        check_pins.urllib.request.urlopen, check_pins.time.sleep = real
    return result, len(calls), sleeps


result, calls, sleeps = run([http(429, "3"), "ok"])
if (result, calls, sleeps) != ("ok", 2, [3]):
    errors.append(f"a 429 then success should retry once after 3 s, got {result!r}, {calls} calls, sleeps {sleeps}")
result, calls, _ = run([http(503), http(503)])
if not isinstance(result, urllib.error.HTTPError) or calls != 2:
    errors.append(f"two 503s should fail after one retry, got {result!r} after {calls} calls")
result, calls, sleeps = run([http(404)])
if not isinstance(result, urllib.error.HTTPError) or calls != 1 or sleeps:
    errors.append(f"a 404 should fail at once, got {result!r} after {calls} calls")

if errors:
    print("\n".join(errors))
    print(f"RESULT FAIL ({len(errors)} errors)")
    sys.exit(1)
print("RESULT PASS (pin check retries: 9 errors classified, 3 fetch sequences)")
