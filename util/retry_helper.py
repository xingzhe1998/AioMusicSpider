import asyncio
import random
from functools import wraps
from loguru import logger
import traceback


class RetryTimeout(Exception):
    def __init__(self, info):
        self.info = info

    def __str__(self):
        return self.info


def aio_retry(**kwargs):
    max_sleep_time: int = kwargs.pop("max", None)
    min_sleep_time: int = kwargs.pop("min", 0)
    attempts: int = kwargs.pop("attempts", 3)
    error: bool = kwargs.pop("error", False)

    def retry(func):
        @wraps(func)
        async def decorator(*args, **kwargs):
            retry_count = 1
            error_info = ""
            while True:
                if retry_count > attempts:
                    if error:
                        raise RetryTimeout("错误次数太多")
                    else:
                        logger.error(f"重试{retry_count}次仍然出错,错误内容,{error_info}")
                        break
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception as e:
                    retry_count += 1
                    if retry_count == attempts:
                        error_info = f"{traceback.format_exc()}"
                    if max_sleep_time:
                        sleep_time = random.randint(min_sleep_time, max_sleep_time)
                        await asyncio.sleep(sleep_time)

        return decorator

    return retry
