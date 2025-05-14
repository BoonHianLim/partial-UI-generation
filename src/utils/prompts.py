from src.utils.utils import rescale_image_loader


def get_sketch_system_message() -> str:
    return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with the HTML code of the current webpage, as well as a screenshot of the new webpage design. Note that some components are in sketch format in the screenshot.
Your task is to convert the new design into HTML and CSS code, based on the provided screenshot and the existing HTML code. You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself. 
Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout. 
If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
You should aim to make the new webpage as responsive as possible. '''


def get_sketch_user_prompt(existing_html_code: str) -> str:
    return '''Here is a screenshot of the new design for the webpage, as well as the existing HTML and CSS code. Please update the HTML and CSS code accordingly to the screenshot. Make sure to maintain the overall layout and design consistency.
    \n''' + existing_html_code


def get_sketch_combined_prompt(existing_html_code: str) -> str:
    return get_sketch_system_message() + "\n" + get_sketch_user_prompt(existing_html_code)


def get_sketch_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_sketch_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]


def get_combined_sketch_user_prompt_with_base64_images(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_sketch_system_message() + "\n" + get_sketch_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]

def get_sketch_with_missing_system_message() -> str:
    return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with the HTML code of the current webpage, as well as a screenshot of the new webpage design. Note that some components are in sketch format in the screenshot.
Some components in the new design are missing and need to be generated.
Your task is to convert identify the missing components in the new design and generate the HTML and CSS code for them, based on the provided screenshot and the existing HTML code. There is one single <missing></missing> tag in the existing HTML code which the new components should be inserted into, and you must replace it with the HTML code based on the sketch in the screenshot.
You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself.
Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
You should aim to make the new webpage as responsive as possible. You must response with only the final HTML + CSS code in one piece, and nothing else.'''

def get_sketch_with_missing_user_prompt(existing_html_code: str) -> str:
    return '''Here is a screenshot of the new design for the webpage, as well as the existing HTML and CSS code. Please update the HTML and CSS code accordingly to the screenshot. Make sure to maintain the overall layout and design consistency. You must response with only the final HTML + CSS code in one piece, and nothing else.
    \n''' + existing_html_code

def  get_sketch_with_missing_combined_prompt(existing_html_code: str) -> str:
    return get_sketch_with_missing_system_message() + "\n" + get_sketch_with_missing_user_prompt(existing_html_code)

def get_sketch_with_missing_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_sketch_with_missing_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]
def get_sketch_with_missing_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_sketch_with_missing_system_message() + "\n" + get_sketch_with_missing_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]
def get_sketch_only_system_prompt() -> str:
    return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with the HTML code of the current webpage, as well as a sketch of partial new webpage design. 
Your task is to convert the sketch into HTML and CSS code, and insert it into the existing HTML code. There is one single <missing></missing> tag in the existing HTML code, and you must replace it with the HTML code of the sketch.
You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself.
Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
You should aim to make the new webpage as responsive as possible. You must response with only the final HTML + CSS code in one piece, and nothing else.'''

def get_sketch_only_user_prompt(existing_html_code: str) -> str:
    return '''Here is a screenshot of the sketch of partial new webpage design, as well as the existing HTML and CSS code. Please update the HTML and CSS code accordingly to the screenshot. Make sure to maintain the overall layout and design consistency. You must response with only the final HTML + CSS code in one piece, and nothing else.
    \n''' + existing_html_code

def get_sketch_only_combined_prompt(existing_html_code: str) -> str:
    return get_sketch_only_system_prompt() + "\n" + get_sketch_only_user_prompt(existing_html_code)

def get_sketch_only_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_sketch_only_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]

def get_sketch_only_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_sketch_only_system_prompt() + "\n" + get_sketch_only_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]

def get_design_system_message() -> str:
    return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with the HTML code of the current webpage, as well as a screenshot of the new webpage design.
Your task is to convert the new design into HTML and CSS code, based on the provided screenshot and the existing HTML code. You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself.
Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
You should aim to make the new webpage as responsive as possible. You must response with only the final HTML + CSS code in one piece, and nothing else.'''


def get_design_user_prompt(existing_html_code: str) -> str:
    return '''Here is a screenshot of the new design for the webpage, as well as the existing HTML and CSS code. Please update the HTML and CSS code accordingly to the screenshot. Make sure to maintain the overall layout and design consistency. You must response with only the final HTML + CSS code in one piece, and nothing else.
    \n''' + existing_html_code


def get_design_combined_prompt(existing_html_code: str) -> str:
    return get_design_system_message() + "\n" + get_design_user_prompt(existing_html_code)


def get_design_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_design_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]


def get_design_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_design_system_message() + "\n" + get_design_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]


def get_design_with_missing_system_message() -> str:
    return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with the HTML code of the current webpage, as well as a screenshot of the new webpage design. 
Some components in the new design are missing and need to be generated. 
Your task is to convert identify the missing components in the new design and generate the HTML and CSS code for them, based on the provided screenshot and the existing HTML code. There is one single <missing></missing> tag in the existing HTML code which the new components should be inserted into, and you must replace it with the HTML code of the new design.
You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself.
Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
You should aim to make the new webpage as responsive as possible. You must response with only the final HTML + CSS code in one piece, and nothing else.'''


def get_design_with_missing_user_prompt(existing_html_code: str) -> str:
    return '''Here is a screenshot of the new design for the webpage, as well as the existing HTML and CSS code. Please update the HTML and CSS code accordingly to the screenshot. Make sure to maintain the overall layout and design consistency. You must response with only the final HTML + CSS code in one piece, and nothing else.
    \n''' + existing_html_code

def get_design_with_missing_combined_prompt(existing_html_code: str) -> str:
    return get_design_with_missing_system_message() + "\n" + get_design_with_missing_user_prompt(existing_html_code)

def get_design_with_missing_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_design_with_missing_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]

def get_design_with_missing_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_design_with_missing_system_message() + "\n" + get_design_with_missing_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]

def get_design_only_system_prompt() -> str:
    return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you with the HTML code of the current webpage, as well as a screenshot of partial new webpage design.
Your task is to convert the partial new design into HTML and CSS code, and insert it into the existing HTML code. There is one single <missing></missing> tag in the existing HTML code, and you must replace it with the HTML code of the partial design.
You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself.
Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
You should aim to make the new webpage as responsive as possible. You must response with only the final HTML + CSS code in one piece, and nothing else.'''


def get_design_only_user_prompt(existing_html_code: str) -> str:
    return '''Here is a screenshot of the partial new design for the webpage, as well as the existing HTML and CSS code. Please update the HTML and CSS code accordingly to the screenshot. Make sure to maintain the overall layout and design consistency. You must response with only the final HTML + CSS code in one piece, and nothing else.
    \n''' + existing_html_code


def get_design_only_combined_prompt(existing_html_code: str) -> str:
    return get_design_only_system_prompt() + "\n" + get_design_only_user_prompt(existing_html_code)


def get_design_only_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_design_only_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]


def get_design_only_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
    return [
        {
            "type": "text",
            "text": get_design_only_system_prompt() + "\n" + get_design_only_user_prompt(existing_html_code)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
            }
        }
    ]


# def get_design_split_system_prompt() -> str:
#     return '''You are an expert web developer who specializes in HTML and CSS. A user will provide you a screenshot of partial new webpage design.
# Your task is to convert the partial new design into a snippet of HTML and CSS code as a component, which can be inserted into another existing HTML later. 
# You should output the HTML first, then output the CSS code.
# Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
# If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
# You should aim to make the component as responsive as possible. '''


# def get_design_split_user_prompt(existing_html_code: str) -> str:
#     return '''Here is a screenshot of the partial new design for the webpage. Please generate the HTML and CSS code accordingly to the screenshot.
#     \n''' + existing_html_code


# def get_design_split_combined_prompt(existing_html_code: str) -> str:
#     return get_design_split_system_prompt() + "\n" + get_design_split_user_prompt(existing_html_code)


# def get_design_split_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
#     return [
#         {
#             "type": "text",
#             "text": get_design_split_user_prompt(existing_html_code)
#         },
#         {
#             "type": "image_url",
#             "image_url": {
#                 "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
#             }
#         }
#     ]


# def get_design_split_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
#     return [
#         {
#             "type": "text",
#             "text": get_design_split_system_prompt() + "\n" + get_design_split_user_prompt(existing_html_code)
#         },
#         {
#             "type": "image_url",
#             "image_url": {
#                 "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
#             }
#         }
#     ]


# def get_design_split_merge_system_prompt() -> str:
#     return '''You are an expert web developer who specializes in HTML and CSS. A user provides you a existing HTML code, as well as a snippet of HTML and CSS code as a component.
# Your task is to merge the component into the existing HTML code, by replacing the <missing></missing> tag in the existing HTML code with the HTML code of the component.
# You may make any necessary changes to the HTML and CSS code of the component to make it fit well into the existing HTML code.
# You should modify only the necessary part, leaving the rest of the page unchanged. Include all CSS code in the HTML file itself.
# Do not hallucinate any dependencies to external files. Pay attention to things like size and position of all the elements, as well as the overall layout.
# If you need to include new images, use "temp.jpg" as the placeholder name. As a reminder, the "temp.jpg" placeholder is very large (1920 x 1080). So make sure to always specify the correct dimensions for the images in your HTML code, since otherwise the image would likely take up the entire page.
# You should aim to make the new webpage as responsive as possible.
# '''


# def get_design_split_merge_user_prompt(partial_html_code: str, existing_html_code: str) -> str:
#     return f'''Here is the existing HTML code, as well as the snippet of HTML and CSS code as a component. Please merge the component into the existing HTML code, by replacing the <missing></missing> tag in the existing HTML code with the HTML code of the component.
# Remember you may make any necessary changes to the HTML and CSS code of the component to make it fit well into the existing HTML code.
# \nSnippet
# ```
# {partial_html_code}
# ```

# Existing HTML
# ```
# {existing_html_code}
# ```'''

# def get_design_split_merge_combined_prompt(partial_html_code: str, existing_html_code: str) -> str:
#     return get_design_split_merge_system_prompt() + "\n" + get_design_split_merge_user_prompt(partial_html_code, existing_html_code)

# def get_design_split_merge_user_prompt_with_base64_images_v1(existing_html_code, sketch_path):
#     return [
#         {
#             "type": "text",
#             "text": get_design_split_merge_user_prompt(existing_html_code)
#         },
#         {
#             "type": "image_url",
#             "image_url": {
#                 "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
#             }
#         }
#     ]

# def get_design_split_merge_combined_user_prompt_with_base64_images(existing_html_code, sketch_path):
#     return [
#         {
#             "type": "text",
#             "text": get_design_split_merge_system_prompt() + "\n" + get_design_split_merge_user_prompt(existing_html_code)
#         },
#         {
#             "type": "image_url",
#             "image_url": {
#                 "url": f"data:image/png;base64,{rescale_image_loader(sketch_path)}"
#             }
#         }
#     ]
