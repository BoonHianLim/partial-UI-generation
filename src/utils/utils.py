import base64
from io import BytesIO
import logging
import os
import re
from PIL import Image

logger: logging.Logger = logging.getLogger(__name__)

def remove_html_comments(html_content):
    comment_pattern = r'<!.*?>'
    html_content = re.sub(comment_pattern, '', html_content, flags=re.DOTALL)
    # html_content = re.sub(r'/\*\*\*.*?\*\*\*/', '',
    #                       html_content, flags=re.DOTALL)
    return html_content.strip()

def read_html(html_path):
    with open(html_path, "r", encoding="utf-8", errors="replace") as html_file:
        return html_file.read()

def extract_html_substring(input_str: str) -> str | None:
    # Regular expression to match the "<html>" tag at the start and capture everything after it
    regex = r"<(.+?)(\s+[^>]*)?>([\s\S]*?)<\/\1>"
    # DOTALL allows matching across multiple lines
    matches = re.findall(regex, input_str, re.DOTALL)

    filtered_matches = [(tag, attrs, content)
                        for tag, attrs, content in matches if tag.lower() != "think"]

    # Return the matched substring(s) joined by newlines, or None if no match is found
    return minify_html('\n'.join(f"<{tag}{attrs or ''}>{content}</{tag}>" for tag, attrs, content in filtered_matches)) if filtered_matches else None

# Remove excessive spaces, newlines, and indentation
def minify_html(html):
    # Replace multiple spaces/newlines with a single space
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r">\s+<", "><", html)  # Remove spaces between tags
    return html.strip()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def remove_missing_tags(html_str: str) -> str:
    # Remove <missing></missing> tags
    return re.sub(r'<missing>.*</missing>', '', html_str)

def validate_html_in_dir(target_dir: str) -> bool:
    all_file = os.listdir(target_dir)

    for file in all_file:
        if file.endswith(".html") and not file.endswith("partial.html"):
            # verify if the partial file exist
            partial_file = file.replace(".html", "_partial.html")
            if partial_file not in all_file:
                logger.fatal(
                    f"Partial file {partial_file} not found for {file}. Skipping.")
                return False

            # verify if partial html file has <missing></missing> tag
            with open(os.path.join(target_dir, partial_file), "r", encoding="utf-8") as f:
                partial_html_content = f.read()
                if "<missing></missing>" not in minify_html(partial_html_content):
                    logger.fatal(
                        f"<missing></missing> tag not found in {partial_file}. Skipping.")
                    return False

            # verify if the png exist
            png_file = file.replace(".html", ".png")
            if png_file not in all_file:
                logger.fatal(
                    f"Image {png_file} not found for {file}. Skipping.")
                return False
            # verify if the partial-design.png exist
            partial_image = file.replace(".html", "_partial-design.png")
            if partial_image not in all_file:
                logger.fatal(
                    f"Partial image {partial_image} not found for {file}. Skipping.")
                return False

            # verify if the partial-design-full.png exist
            partial_image_full = file.replace(".html", "_partial-design-full.png")
            if partial_image_full not in all_file:
                logger.fatal(
                    f"Partial image full {partial_image_full} not found for {file}. Skipping.")
                return False

def rescale(image_path):
    with Image.open(image_path) as img:
        # Get original dimensions
        width, height = img.size

        # Determine the short side
        short_side = min(width, height)
        long_side = max(width, height)

        # Check if resizing is needed
        if short_side <= 768:
            if long_side > 2000:
                logger.warning(f"Bad aspect ratio for GPT-4V: {image_path}")
            else:
                return Image.open(BytesIO(open(image_path, "rb").read()))

        # Calculate new dimensions
        scaling_factor = 768 / short_side
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)

        # Check if the long side exceeds 2000 pixels after rescaling
        if new_width > 2000 or new_height > 2000:
            logger.warning(
                f"Bad aspect ratio for GPT-4V after rescaling: {image_path}")

        # Resize the image
        resized_img = img.resize(
            (new_width, new_height), Image.Resampling.LANCZOS)
        return resized_img
    
def rescale_image_loader_image_path(image_path):
    """
    Load an image, rescale it so that the short side is 768 pixels.
    If after rescaling, the long side is more than 2000 pixels, return None.
    If the original short side is already shorter than 768 pixels, no rescaling is done.

    Args:
    image_path (str): The path to the image file.

    Returns:
    Image or None: The rescaled image or None if the long side exceeds 2000 pixels after rescaling.
    """
    resized_img = rescale(image_path)
    resized_img = resized_img.save(
        image_path.replace(".png", "_rescaled.png"))
    
    return image_path.replace(".png", "_rescaled.png")

def rescale_image_loader_image(image_path):
    return rescale(image_path)

def rescale_image_loader(image_path):
    """
    Load an image, rescale it so that the short side is 768 pixels.
    If after rescaling, the long side is more than 2000 pixels, return None.
    If the original short side is already shorter than 768 pixels, no rescaling is done.

    Args:
    image_path (str): The path to the image file.

    Returns:
    Image or None: The rescaled image or None if the long side exceeds 2000 pixels after rescaling.
    """
    resized_img = rescale(image_path)
    resized_img = resized_img.save(
        image_path.replace(".png", "_rescaled.png"))
    base64_image = encode_image(
        image_path.replace(".png", "_rescaled.png"))
    os.remove(image_path.replace(".png", "_rescaled.png"))

    return base64_image
