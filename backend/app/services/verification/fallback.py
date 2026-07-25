from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from typing import TypeVar


ResultT = TypeVar("ResultT")


class FallbackProvider:
    """Runs a replaceable provider with a bounded wait and deterministic fallback."""

    def execute(
        self,
        operation: Callable[[], ResultT],
        fallback: Callable[[Exception], ResultT],
        timeout_seconds: float = 2.0,
    ) -> ResultT:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(operation)
        try:
            return future.result(timeout=timeout_seconds)
        except FutureTimeoutError as exc:
            future.cancel()
            return fallback(exc)
        except Exception as exc:  # Provider boundaries must not take down the API.
            return fallback(exc)
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
