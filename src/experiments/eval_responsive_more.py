import argparse
import json
import logging
import os
import time

import pandas as pd

from src.metrics.visual_score import visual_eval_v3_multi
from src.utils.logger import setup_logger, suppress_module_logging

logger: logging.Logger = logging.getLogger(__name__)


class Viewport():
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        return f"{self.width}x{self.height}"

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

    def __eq__(self, value):
        if isinstance(value, Viewport):
            return self.width == value.width and self.height == value.height
        return False

    def __hash__(self):
        return hash((self.width, self.height))

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height
        }

    @staticmethod
    def from_str(viewport_str: str) -> 'Viewport':
        width, height = map(int, viewport_str.split('x'))
        return Viewport(width, height)


def read_viewports_from_csv(csv_path: str) -> set[Viewport]:
    logger.info("Reading viewports from csv: %s", csv_path)
    df = pd.read_csv(csv_path)
    res = set()
    for e in df.iloc[:, 0]:
        if "x" in e:
            res.add(Viewport.from_str(e))
    return res


def eval_responsive(original_dir: str, generated_dir: str, viewport: Viewport, visited_files: set[str]) -> list[dict]:
    generated_files = os.listdir(generated_dir)
    # read res dict in json
    generated_res_dict = {}
    res_dicts = []
    if not os.path.exists(os.path.join(generated_dir, 'res_dict.json')):
        logger.info("res_dict.json does not exist.")
        raise FileNotFoundError(
            f"res_dict.json does not exist in {generated_dir}.")

    with open(os.path.join(generated_dir, 'res_dict.json'), 'r') as f:
        generated_res_dict = json.load(f)
    generated_res_dict = {item["id"].split(
        '_', 1)[0]: item for item in generated_res_dict}

    for filename in generated_files:
        if filename in visited_files:
            logger.info(f"Skipping visited file: {filename}.")
            continue

        if not filename.endswith('.html'):
            continue

        if filename.endswith('_p.html'):
            logger.warning(
                f"Skipping temporary file: {filename}.")
            try:
                os.remove(os.path.join(generated_dir, filename))
            except Exception as e:
                logger.error(
                    f"Error removing temporary file {filename}: {e}")
            continue
        if filename.endswith('_p_1.html'):
            logger.warning(
                f"Skipping temporary file: {filename}.")
            try:
                os.remove(os.path.join(generated_dir, filename))
            except Exception as e:
                logger.error(
                    f"Error removing temporary file {filename}: {e}")
            continue

        img_id = filename.split('_')[0]
        original_html_path = os.path.join(
            original_dir, img_id + '.html')
        generated_html_path = os.path.join(generated_dir, filename)

        if not os.path.exists(original_html_path):
            logger.error(
                f"For {img_id}, original html file does not exist. This should never happen unless you remove data from the original dataset, or you specify the wrong datasets. No evaluation will be done.")
            continue

        if not os.path.exists(generated_html_path):
            logger.error(
                f"For {img_id}, generated html file does not exist. Probably because that your experiment directory has temporary file ending with _p. Skipping evaluation.")
            continue

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
            "try_count": generated_res_dict[img_id]["try_count"],
        }
        logger.info(
            f"res_dict for {img_id} with viewport {viewport}: {res_dict}")
        res_dicts.append(res_dict)
    return res_dicts


if __name__ == "__main__":
    setup_logger(log_file_prefix="responsive_eval")
    suppress_module_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--original_dir', type=str,
                        default='/juice2/scr2/nlp/pix2code/zyanzhe/sketch2code_dataset_v1')
    parser.add_argument('--generated_dir', type=str)
    parser.add_argument('--viewports_dir', type=str,
                        default='src/datasets/viewport')
    args = parser.parse_args()
    logger.info(f"args: {args}")
    assert args.generated_dir is not None and isinstance(
        args.generated_dir, str), "Generated directory is not valid"
    assert args.original_dir is not None and isinstance(
        args.original_dir, str), "Original directory is not valid"
    assert args.viewports_dir is not None and isinstance(
        args.viewports_dir, str), "Viewports csv is not valid"

    original_dir = args.original_dir
    generated_dir = args.generated_dir
    viewports_dir = args.viewports_dir

    current_datetime = time.strftime("%Y%m%d-%H%M%S")

    unique_viewports: set[Viewport] = set()
    viewports_dict: dict[str, set] = {}
    res_dicts: dict[str, dict] = {}

    viewports_csvs = os.listdir(viewports_dir)
    visited_files = set()
    for csv in viewports_csvs:
        viewports_csv = os.path.join(viewports_dir, csv)
        csv_name = os.path.basename(csv).split('.')[0]

        viewports = read_viewports_from_csv(viewports_csv)
        unique_viewports.update(viewports)
        viewports_dict[csv_name] = viewports
        res_dicts[csv_name] = {}

    for csv in viewports_csvs:
        csv_name = os.path.basename(csv).split('.')[0]

        visited_dicts: dict[str, list[dict]] = {}
        generated_json = os.path.join(
            generated_dir, 'res_dict_eval__' + csv_name + '.json')
        if os.path.exists(generated_json):
            with open(generated_json, 'r') as f:
                visited_dicts = json.load(f)
                # add to res_dicts
            res_dicts[csv_name] = visited_dicts
            for item_list in visited_dicts.values():
                for item in item_list:
                    visited_files.add(item["filename"])

    logger.info(f"Unique viewports: {unique_viewports}")
    logger.info(f"Viewports dict: {viewports_dict}")
    logger.debug(f"Res dicts: {res_dicts}")

    for viewport in unique_viewports:
        res_dict_key = str(viewport)
        logger.info(f"Evaluating for viewport: {res_dict_key}")

        viewport_result_list = eval_responsive(
            original_dir, generated_dir, viewport, visited_files)
        logger.info(f"viewport_result_list: {viewport_result_list}")

        for csv_name, viewport_set in viewports_dict.items():
            if viewport in viewport_set:
                if res_dict_key not in res_dicts[csv_name]:
                    res_dicts[csv_name][res_dict_key] = []
                res_dicts[csv_name][res_dict_key].extend(viewport_result_list)

            with open(os.path.join(generated_dir, 'res_dict_eval__' + csv_name + '.json'), 'w') as f:
                json.dump(res_dicts[csv_name], f, indent=4)
