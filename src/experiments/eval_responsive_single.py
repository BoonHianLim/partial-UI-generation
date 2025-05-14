import argparse
import json
import logging
import os
import time

import pandas as pd

from src.metrics.visual_score import visual_eval_v3_multi
from src.utils.logger import setup_logger, suppress_module_logging
from src.experiments.eval_responsive import Viewport

logger: logging.Logger = logging.getLogger(__name__)


def eval_responsive_single(original_dir: str, generated_dir: str, viewport: Viewport, filename: str):
    if not filename.endswith('.html'):
        return None

    if filename.endswith('_p.html'):
        logger.warning(
            f"Skipping temporary file: {filename}.")
        try:
            os.remove(os.path.join(generated_dir, filename))
        except Exception as e:
            logger.error(
                f"Error removing temporary file {filename}: {e}")
        return None

    if filename.endswith('_p_1.html'):
        logger.warning(
            f"Skipping temporary file: {filename}.")
        try:
            os.remove(os.path.join(generated_dir, filename))
        except Exception as e:
            logger.error(
                f"Error removing temporary file {filename}: {e}")
        return None

    img_id = filename.split('_')[0]
    original_html_path = os.path.join(
        original_dir, img_id + '.html')
    generated_html_path = os.path.join(generated_dir, filename)

    if not os.path.exists(original_html_path):
        logger.error(
            f"For {img_id}, original html file does not exist. This should never happen unless you remove data from the original dataset, or you specify the wrong datasets. No evaluation will be done.")
        return None

    if not os.path.exists(generated_html_path):
        logger.error(
            f"For {img_id}, generated html file does not exist. Probably because that your experiment directory has temporary file ending with _p. Skipping evaluation.")
        return None

    result = visual_eval_v3_multi(
        [[generated_html_path], original_html_path], viewport=viewport.to_dict())
    sum_sum_areas, final_score, (size_score, text_score,
                                 position_score, color_score, clip_score) = result[0]

    res_dict = {
        "id": img_id,
        "filename": filename,
        "sum_sum_areas": sum_sum_areas,
        "final_score": final_score,
        "size_score": size_score,
        "text_score": text_score,
        "position_score": position_score,
        "color_score": color_score,
        "clip_score": clip_score,
    }
    logger.info(f"res_dict for {img_id} with viewport {viewport}: {res_dict}")
    return res_dict


if __name__ == "__main__":
    setup_logger(log_file_prefix="responsive_eval")
    suppress_module_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--original_dir', type=str,
                        default='/juice2/scr2/nlp/pix2code/zyanzhe/sketch2code_dataset_v1')
    parser.add_argument('--generated_dir', type=str)
    parser.add_argument('--viewport', type=str)
    parser.add_argument('--filename', type=str)
    args = parser.parse_args()
    logger.info(f"args: {args}")

    eval_responsive_single(
        original_dir=args.original_dir,
        generated_dir=args.generated_dir,
        viewport=Viewport.from_str(args.viewport),
        filename=args.filename
    )
