import argparse
import os
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import ebooklib
from ebooklib import epub
import tempfile

# Specify the path to your custom tessdata directory
custom_tessdata_dir = os.path.abspath('./custom_tessdata')

def perform_ocr(image):
    try:
        return pytesseract.image_to_string(
            image, 
            lang='ben+eng',  # Use both Bengali and English
            config=f'--tessdata-dir "{custom_tessdata_dir}"'
        )
    except pytesseract.TesseractError as e:
        print(f"OCR Error: {str(e)}")
        return ""

def process_pdf(pdf_file):
    with open(pdf_file, 'rb') as file:
        pdf_bytes = file.read()
    images = convert_from_bytes(pdf_bytes)
    all_text = []
    for i, image in enumerate(images):
        print(f"Processing page {i+1} of {len(images)}...")
        text = perform_ocr(image)
        all_text.append(text)
    
    return "\n\n".join(all_text)

def create_xhtml(text, output_file):
    paragraphs = text.split("\n\n")
    
    xhtml_content = '<?xml version="1.0" encoding="utf-8"?>\n'
    xhtml_content += '<!DOCTYPE html>\n\n'
    xhtml_content += '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
    xhtml_content += '<head>\n'
    xhtml_content += '  <title></title>\n'
    xhtml_content += '</head>\n\n'
    xhtml_content += '<body>\n'
    
    for paragraph in paragraphs:
        xhtml_content += f'  <p>{paragraph.strip()}</p>\n'
    
    xhtml_content += '</body>\n'
    xhtml_content += '</html>'
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(xhtml_content)

def process_folder(folder_path):
    output_folder = os.path.join(folder_path, "xhtml_output")
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_file = os.path.join(folder_path, filename)
            print(f"Processing file: {pdf_file}")
            
            try:
                full_text = process_pdf(pdf_file)
                output_file = os.path.join(output_folder, os.path.splitext(filename)[0] + ".xhtml")
                create_xhtml(full_text, output_file)
                print(f"XHTML file created: {output_file}")
            except Exception as e:
                print(f"An error occurred while processing {pdf_file}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR PDFs and create XHTML files")
    parser.add_argument("folder_path", help="Path to the folder containing PDF files")
    args = parser.parse_args()

    process_folder(args.folder_path)
