"""Logger Utility Module

Configures application logging with file and console handlers.
"""

import logging
import logging.handlers
import os
from config import Config


def setup_logger(
    name: str = None,
    log_level: str = None,
    log_file: str = None
) -> logging.Logger:
    """
    Setup and configure application logger.
    
    Args:
        name (str, optional): Logger name
        log_level (str, optional): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str, optional): Log file path
    
    Returns:
        logging.Logger: Configured logger instance
    """
    name = name or __name__
    log_level = log_level or Config.LOG_LEVEL
    log_file = log_file or Config.LOG_FILE
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f'Warning: Could not create log directory: {e}')
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler (with rotation)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=Config.LOG_MAX_BYTES,
            backupCount=Config.LOG_BACKUP_COUNT
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f'Warning: Could not setup file logging: {e}')
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name (str, optional): Logger name (usually __name__)
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name or __name__)


def log_function_call(func):
    """
    Decorator to log function calls and execution time.
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f'Calling {func.__name__}')
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f'{func.__name__} completed in {duration:.3f}s')
            return result
        except Exception as e:
            logger.error(f'{func.__name__} failed: {str(e)}', exc_info=True)
            raise
    
    return wrapper


class LogContextFilter(logging.Filter):
    """
    Filter to add context information to log records.
    """
    
    def __init__(self, context: dict = None):
        """
        Initialize context filter.
        
        Args:
            context (dict, optional): Context dictionary
        """
        super().__init__()
        self.context = context or {}
    
    def filter(self, record):
        """
        Add context to log record.
        
        Args:
            record: Log record
        
        Returns:
            bool: Always True to allow record
        """
        for key, value in self.context.items():
            setattr(record, key, value)
        return True
