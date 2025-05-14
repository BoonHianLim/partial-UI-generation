#!/usr/bin/env python
import argparse
import logging
import os
from huggingface_hub import snapshot_download

from src.utils.logger import setup_logger

logger: logging.Logger = logging.getLogger(__name__)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_download_path = os.path.join(parent_dir, "weights")


def download_model(model_id: str, cache_dir: str = default_download_path, revision: str = "main"):
    """
    Downloads the model repository from Hugging Face Hub and returns the local directory path.
    
    Args:
        model_id (str): The repository ID of the model (e.g., "deepseek-ai/deepseek-vl2-small").
        cache_dir (str, optional): Directory to store the downloaded files.
        revision (str): The model revision to download (e.g., "main", a branch, tag, or commit).
        
    Returns:
        str: The path to the downloaded model directory.
    """
    logger.info(f"Downloading model '{model_id}' (revision: {revision})...")
    os.makedirs(cache_dir, exist_ok=True)
    local_dir = snapshot_download(
        repo_id=model_id, cache_dir=cache_dir, revision=revision)
    logger.info(f"Model downloaded successfully to: {local_dir}")
    return local_dir


def main():
    setup_logger()
    
    parser = argparse.ArgumentParser(
        description="Download a model from Hugging Face Hub for offline use with Transformers."
    )
    parser.add_argument(
        "--model_id",
        type=str,
        default="deepseek-ai/deepseek-vl2-small",
        help="The model repository ID on Hugging Face Hub."
    )
    parser.add_argument(
        "--cache_dir",
        type=str,
        default=default_download_path,
        help="(Optional) Directory to store the downloaded model files."
    )
    parser.add_argument(
        "--revision",
        type=str,
        default="main",
        help="The revision (branch, tag, or commit) to download. Default is 'main'."
    )
    args = parser.parse_args()
    download_model(args.model_id, cache_dir=args.cache_dir,
                   revision=args.revision)


if __name__ == "__main__":
    main()
