import logging
import os
import sys
import time

logger: logging.Logger = logging.getLogger(__name__)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_log_default_dir = os.path.join(_parent_dir, 'logs')


def setup_logger(std_debug_level: int = logging.INFO, file_debug_level: int = logging.DEBUG, out_dir: str = _log_default_dir, log_file_prefix = "") -> None:
    """
    Sets up the logger for the project.
    This will log to both stdout and a file.

    This should be called at the beginning of the program.

    By logging to a file, we can keep track of the logs even if the program crashes.

    The default log level is INFO.
    This means that only logs with level INFO or higher will be logged.

    If you want to log DEBUG logs, you can change the log level to DEBUG.
    This will allow you to see the DEBUG logs in the console, which contains more detailed information.
    Not recommended to use DEBUG logs in the competition, it will be too spammy.
    You won't be able to see the important logs.
    
    Parameters:
        std_debug_level (int): The log level for the console.
        file_debug_level (int): The log level for the file.
    
    Returns:
        None
    """
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s: %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(std_debug_level)
    stdout_handler.setFormatter(formatter)
    stdout_configure_error_flag = False
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception as e:
        stdout_configure_error_flag = True
    os.environ["PYTHONIOENCODING"] = "utf-8"

    current_datetime = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(out_dir, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(out_dir, log_file_prefix + current_datetime + '.log'), encoding='utf-8')
    file_handler.setLevel(file_debug_level)
    file_handler.setFormatter(formatter)
    logging.basicConfig(
        handlers=[stdout_handler, file_handler],
        level=min(std_debug_level, file_debug_level))
    logger.info("Logger is up.")
    if stdout_configure_error_flag:
        logger.warning(
            "Failed to reconfigure stdout encoding. Please check your console encoding.")

def suppress_module_logging():
    logging.getLogger("PIL").setLevel(logging.INFO)
    logging.getLogger("colormath").setLevel(logging.INFO)
