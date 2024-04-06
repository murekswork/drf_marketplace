import functools

from logging_.logger import logger


def exception_logging(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Exception occurred {func.__name__}: {e}")

    return wrapper
