import argparse
import os
import re
import pytesseract
from pdf2image import convert_from_bytes
from ebooklib import epub

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

def extract_last_number(filename):
    # Extract the last number or range from the filename
    match = re.search(r'(\d+)(-\d+)?(?=\.pdf$)', filename)
    if match:
        start = int(match.group(1))
        end = int(match.group(2)[1:]) if match.group(2) else start
        return start, end
    return float('inf'), float('inf')  # Return a high value to sort invalid names last

def create_epub_from_ocr(folder_path, output_file):
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title('OCR Result')
    book.set_language('en')
    book.add_author('Generated Author')

    spine = ['nav']
    toc = []

    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    pdf_files.sort(key=lambda f: extract_last_number(f))

    for filename in pdf_files:
        pdf_file = os.path.join(folder_path, filename)
        print(f"Processing file: {pdf_file}")
        
        try:
            full_text = process_pdf(pdf_file)
            if full_text.strip():
                chapter_title = os.path.splitext(filename)[0]
                chapter = epub.EpubHtml(
                    title=chapter_title, 
                    file_name=f'{chapter_title}.xhtml', 
                    lang='en'
                )
                chapter.content = f'<h1>{chapter_title}</h1><p>{full_text}</p>'
                
                book.add_item(chapter)
                spine.append(chapter)
                toc.append(epub.Link(f'{chapter_title}.xhtml', chapter_title, chapter_title))
            else:
                print(f"No text extracted from {filename}")
        except Exception as e:
            print(f"An error occurred while processing {pdf_file}: {str(e)}")
    
    if not toc:
        print("No valid content to add to the EPUB.")
        return

    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    try:
        epub.write_epub(output_file, book, {})
        print(f"EPUB file created: {output_file}")
    except Exception as e:
        print(f"Error writing EPUB: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OCR PDFs and create EPUB")
    parser.add_argument("folder_path", help="Path to the folder containing PDF files")
    args = parser.parse_args()

    output_epub_file = os.path.join(args.folder_path, "ocr_result.epub")
    create_epub_from_ocr(args.folder_path, output_epub_file)