import http.client
import logging
import os
import pickle
import traceback
import json
import time
import argparse
import shutil

from google import genai
from google.genai import types, Client
from google.genai.errors import APIError, ClientError
from tqdm import tqdm

from src.utils.directory import get_default_out_dir, sanitize_model_name
from src.utils.utils import extract_html_substring, minify_html, remove_html_comments, read_html, remove_missing_tags, rescale_image_loader_image
from src.utils.prompts import get_design_only_combined_prompt
from src.utils.logger import setup_logger, suppress_module_logging

logger: logging.Logger = logging.getLogger(__name__)

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_CIVIC_INTEGRITY",
        "threshold": "BLOCK_NONE",
    },
]


def generate(model, client: Client, sketch_path, partial_html_path, source_html_path, out_dir, img_id):
    existing_html = minify_html(
        remove_html_comments(read_html(partial_html_path)))
    logger.info(f"existing html: \n{existing_html[:20]}")

    prompt = get_design_only_combined_prompt(existing_html)
    image = rescale_image_loader_image(sketch_path)
    logger.debug(f"agent_messages: {prompt}")

    assert prompt is not None, "Prompt is None"
    assert image is not None, "Image is None"

    html_response = None
    i = 0
    max_tries = 10

    while not html_response and i < max_tries:
        try:
            i += 1
            response = client.models.generate_content(
                model=model,
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    max_output_tokens=5000,
                    safety_settings=SAFETY_SETTINGS,
                    candidate_count=1,
                )
            )

            output_texts = response.text.strip()

            logger.debug(f"agent: {output_texts}")

            html_response = extract_html_substring(output_texts)
            if not html_response:
                continue

            logger.debug(f"final html: \n{html_response}")
            html_path = os.path.join(out_dir, f'{img_id}_out.html')
            with open(html_path, 'w', encoding="utf-8", errors="replace") as f:
                f.write(html_response)

            res_dict = {
                "id": img_id,
                "filename": html_path,
                "try_count": i
            }

            logger.debug(f"res_dict: {res_dict}")
            return True, res_dict
        except APIError as e:
            if e.status == 429:
                i -= 1
                logger.error(f"Rate limit exceeded, waiting 30 seconds")
                time.sleep(30)
            elif e.status == 504:
                i -= 1
                logger.error(f"Timeout, waiting 3 seconds and retry again")
                time.sleep(3)
            elif e.status == 400 or e.status == 403 or e.status == 404:
                logger.fatal("Webpage generation failed due to API error")
                logger.error(traceback.format_exc())
                raise e  # Unresolvable error by retrying. Raise to stop the program
            else:
                logger.error(
                    f"Webpage generation for {img_id} failed due to {e}")
                logger.error(traceback.format_exc())
                time.sleep(3)
        except ClientError as e:
            if e.code == 429:
                i -= 1
                logger.error(f"Rate limit exceeded, waiting 30 seconds")
                time.sleep(30)
            elif e.code == 504:
                i -= 1
                logger.error(f"Timeout, waiting 3 seconds and retry again")
                time.sleep(3)
            elif e.code == 400 or e.code == 403 or e.code == 404:
                logger.fatal("Webpage generation failed due to API error")
                logger.error(traceback.format_exc())
                raise e  # Unresolvable error by retrying. Raise to stop the program
            else:
                logger.error(
                    f"Webpage generation for {img_id} failed due to {e}")
                logger.error(traceback.format_exc())
                time.sleep(3)
        except http.client.RemoteDisconnected:
            i -= 1
            logger.error(
                f"Remote disconnected when generating webpage for {img_id}, retrying")
            time.sleep(3)
        except Exception as e:
            logger.error(f"Webpage generation for {img_id} failed due to {e}")
            logger.error(traceback.format_exc())
            time.sleep(3)
    return False, {}


if __name__ == "__main__":
    FILE_NAME = os.path.basename(__file__)
    setup_logger()
    suppress_module_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='gpt-4o')
    parser.add_argument('--input_dir', type=str,
                        default='/juice2/scr2/nlp/pix2code/zyanzhe/sketch2code_dataset_v1')
    parser.add_argument('--out_dir', type=str)
    parser.add_argument('--endpoint', type=str)
    parser.add_argument('--api_key', type=str)
    parser.add_argument('--starts_from', type=int, default=0)
    parser.add_argument('--load_from_cache',
                        action=argparse.BooleanOptionalAction)
    parser.add_argument(
        "--sanity_check", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    logger.info(f"args: {args}")
    assert "model" in args, "model is not in args"

    if not args.out_dir:
        args.out_dir = get_default_out_dir(
            FILE_NAME, sanitize_model_name(args.model))

    endpoint = args.endpoint
    api_key = args.api_key

    client = genai.Client(api_key=api_key)

    database = {}
    skip_count = 0
    load_from_cache = args.load_from_cache
    if load_from_cache:
        logger.info("loading from cache.")
        database = pickle.load(open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), f'./cache/{FILE_NAME}.pkl'), 'rb'))
        skip_count = database["processed_img_id_count"]
    else:
        database["input_dir"] = args.input_dir
        database["out_dir"] = args.out_dir
        database["model"] = args.model

        os.makedirs(database["out_dir"], exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), './cache/'), exist_ok=True)
        # copy "temp.jpg" to the target directory
        source_image_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "temp.jpg")
        destination_image_path = os.path.join(database["out_dir"], "temp.jpg")
        shutil.copy(source_image_path, destination_image_path)

        all_files = os.listdir(database["input_dir"])
        if args.sanity_check:
            all_files = all_files[:5]
            logger.info(all_files)

        examples = {}

        for filename in all_files:
            if '_' in filename and filename.endswith('partial-design.png'):
                parts = filename.split('_')
                img_id = parts[0]

                if img_id not in examples:
                    examples[img_id] = []

                examples[img_id].append(filename)

        starts_from = args.starts_from

        database["starts_from"] = starts_from
        database["examples"] = examples
        database["num_success"] = 0
        database["processed_img_id_count"] = 0
        database["total"] = 0
        database["res_dicts"] = []

    logger.info("found examples: %d", len(database["examples"]))

    for img_id in tqdm(sorted(database["examples"])):
        if skip_count > 0:
            logger.warning(f"assume {img_id} has been processed, skipping")
            skip_count -= 1
            continue

        logger.info(f"processing img id {img_id}")
        partial_html_path = os.path.join(
            database["input_dir"], f'{img_id}_partial.html')
        html_path = os.path.join(database["input_dir"], f'{img_id}.html')
        for sketch_file in database["examples"][img_id]:
            sketch_id = sketch_file.split('_')[0]
            database["total"] += 1
            sketch_path = os.path.join(database["input_dir"], sketch_file)
            success, res_dict = generate(
                database["model"], client, sketch_path, partial_html_path, html_path, database["out_dir"], sketch_id)

            if success:
                database["num_success"] += 1
                database["res_dicts"].append(res_dict)
                logger.info(f"successfully generated webpage for {sketch_id}")
            else:
                logger.error(f"failed to generate webpage for {sketch_id}")

        if database["num_success"] % 10 == 0:
            with open(os.path.join(database["out_dir"], 'res_dict.json'), "w") as f:
                json.dump(database["res_dicts"], f, indent=4)

        logger.info(f"img id {img_id} has been processed. Saving to cache.")
        database["processed_img_id_count"] += 1
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'./cache/{FILE_NAME}.pkl'), 'wb') as f:
            pickle.dump(database, f)
    with open(os.path.join(database["out_dir"], 'res_dict.json'), "w") as f:
        json.dump(database["res_dicts"], f, indent=4)

    logger.info(
        f'All done. {database["num_success"]} out of {database["total"]} successful generations.')
