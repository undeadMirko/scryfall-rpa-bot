import time
from typing import Callable, Any
from functools import wraps
from src.logger import logger

def retry(max_retries: int = 3, delay: int = 2, backoff: int = 2):
    """
    Decorator for adding retry logic with exponential backoff to functions.
    
    :param max_retries: Maximum number of times to retry before raising an exception.
    :param delay: Initial delay in seconds between retries.
    :param backoff: Multiplier for the delay after each retry.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {str(e)}")
                    if attempt == max_retries:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}.")
                        raise e
                    logger.info(f"Retrying in {current_delay} seconds...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
