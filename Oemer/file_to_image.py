import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF for PDF handling
import json
import yaml
import textwrap

def text_to_image(text, output_path, width=1200, font_size=16, bg_color=(255, 255, 255), text_color=(0, 0, 0)):
    """Convert text content to an image"""
    # Calculate required height based on text content
    font = ImageFont.truetype("arial.ttf", font_size)
    padding = 20
    line_height = font_size + 4
    
    # Wrap text to fit width
    wrapper = textwrap.TextWrapper(width=int((width - 2*padding) / (font_size * 0.6)))
    lines = []
    for line in text.split('\n'):
        if line.strip():
            lines.extend(wrapper.wrap(line))
        else:
            lines.append('')
    
    # Create image with appropriate height
    height = len(lines) * line_height + 2 * padding
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text
    y_position = padding
    for line in lines:
        draw.text((padding, y_position), line, font=font, fill=text_color)
        y_position += line_height
    
    # Save image
    img.save(output_path)
    return output_path

def pdf_to_image(pdf_path, output_path):
    """Convert first page of PDF to image"""
    # Open the PDF
    doc = fitz.open(pdf_path)
    
    # Get the first page
    page = doc.load_page(0)
    
    # Render page to an image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    
    # Save the image
    pix.save(output_path)
    return output_path

def json_to_image(json_path, output_path):
    """Convert JSON file to a formatted image"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Pretty print the JSON
    formatted_json = json.dumps(data, indent=2)
    
    # Convert to image
    return text_to_image(formatted_json, output_path, bg_color=(240, 248, 255), text_color=(0, 0, 128))

def yaml_to_image(yaml_path, output_path):
    """Convert YAML file to a formatted image"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Convert to YAML string
    formatted_yaml = yaml.dump(data, default_flow_style=False)
    
    # Convert to image
    return text_to_image(formatted_yaml, output_path, bg_color=(248, 248, 240), text_color=(0, 100, 0))

def file_to_image(input_path, output_path=None):
    """Convert a file to an image based on its type"""
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return None
    
    # Determine file extension
    _, ext = os.path.splitext(input_path)
    ext = ext.lower()
    
    # Set default output path if not provided
    if not output_path:
        output_path = os.path.splitext(input_path)[0] + ".png"
    
    try:
        # Process based on file type
        if ext == '.pdf':
            return pdf_to_image(input_path, output_path)
        elif ext == '.json':
            return json_to_image(input_path, output_path)
        elif ext in ['.yml', '.yaml']:
            return yaml_to_image(input_path, output_path)
        else:
            # Default: treat as text file
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return text_to_image(content, output_path)
    
    except Exception as e:
        print(f"Error converting file to image: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert a file to an image')
    parser.add_argument('input_file', help='Path to the input file')
    parser.add_argument('-o', '--output', help='Path to save the output image')
    args = parser.parse_args()
    
    result = file_to_image(args.input_file, args.output)
    
    if result:
        print(f"File successfully converted to image: {result}")
    else:
        print("File conversion failed.")

if __name__ == "__main__":
    main()