import re
import time
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_default_out_dir(type, model_name):
    current_datetime = time.strftime("%Y%m%d-%H%M%S")
    new_out_dir = os.path.join(parent_dir, "experiment-results",
                               f"{type}_{model_name}_{current_datetime}")
    return new_out_dir


def sanitize_model_name(model_name: str) -> str:
    """Replace invalid characters with underscores."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', model_name)
