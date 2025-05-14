import argparse
import logging
import os
import traceback
from playwright.sync_api import sync_playwright
from PIL import Image

logger: logging.Logger = logging.getLogger(__name__)


def take_and_save_screenshot(url, output_file="screenshot.png", do_it_again=False, viewport: dict = {"width": 1280, "height": 720}, max_retries=3):
    # Convert local path to file:// URL if it's a file
    if os.path.exists(url):
        url = "file://" + os.path.abspath(url)

    # whether to overwrite existing screenshots
    if os.path.exists(output_file) and not do_it_again:
        logger.error(f"{output_file} exists! Skipping screenshot.")
        return
    retry_count = 0

    while retry_count < max_retries:
        try:
            with sync_playwright() as p:
                # Choose a browser, e.g., Chromium, Firefox, or WebKit
                browser = p.chromium.launch()
                page = None
                if viewport is None:
                    page = browser.new_page()
                else:
                    page = browser.new_page(viewport=viewport)

                # Navigate to the URL
                page.goto(url, timeout=60000)

                # Take the screenshot
                page.screenshot(path=output_file, full_page=True,
                                animations="disabled", timeout=60000)

                browser.close()

                break
        except Exception as e:
            logger.warning(
                f"Failed to take screenshot due to: {e}. Generating a blank image.")
            logger.warning(traceback.format_exc())
            # Generate a blank image
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(
                    f"Retrying screenshot ({retry_count}/{max_retries})...")
                continue
            else:
                logger.error("Max retries reached. Generating a blank image.")
                img = Image.new(
                    'RGB', (viewport["width"], viewport["height"]), color='white')
                img.save(output_file)
                break

if __name__ == "__main__":
    # Example usage
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True,
                        help='URL or local file path to take a screenshot of')
    parser.add_argument('--output', type=str, default='screenshot.png',
                        help='Output file name for the screenshot')
    parser.add_argument('--do_it_again', action='store_true',
                        help='Whether to overwrite existing screenshots')
    parser.add_argument('--viewport', type=str, default=None,
                        help='Viewport size in the format "width,height"')
    args = parser.parse_args()
    logger.info(f"args: {args}")
    assert args.url is not None and isinstance(
        args.url, str), "URL is not valid"
    assert args.output is not None and isinstance(
        args.output, str), "Output file name is not valid"
    assert args.do_it_again is not None and isinstance(
        args.do_it_again, bool), "Do it again flag is not valid"
    assert args.viewport is not None and isinstance(
        args.viewport, str), "Viewport is not valid"
    assert args.viewport.count("x") == 1, "Viewport should be in the format 'width,height'"

    viewport = args.viewport.split("x")
    viewport = {"width": int(viewport[0]), "height": int(viewport[1])}
    take_and_save_screenshot(args.url, args.output,
                             args.do_it_again, viewport=viewport)
