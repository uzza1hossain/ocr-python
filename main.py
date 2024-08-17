import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os
import ebooklib
from ebooklib import epub
import tempfile

# Initialize session state
if 'full_text' not in st.session_state:
    st.session_state.full_text = ""
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False

# Specify the path to your custom tessdata directory
custom_tessdata_dir = os.path.abspath('./custom_tessdata')

st.title("OCR PDFs and images (Bengali and English)")
st.write("This tool runs OCR on PDFs and images, recognizing both Bengali and English text.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF or image file", type=["pdf", "png", "jpg", "jpeg"])

# Create a placeholder for the processing status
processing_status = st.empty()

# Create a placeholder for the full text
full_text_placeholder = st.empty()

# Create a placeholder for the download buttons
download_buttons_placeholder = st.empty()

def perform_ocr(image):
    try:
        return pytesseract.image_to_string(
            image, 
            lang='ben+eng',  # Use both Bengali and English
            config=f'--tessdata-dir "{custom_tessdata_dir}"'
        )
    except pytesseract.TesseractError as e:
        st.error(f"OCR Error: {str(e)}")
        return ""

def process_image(image_file):
    image = Image.open(image_file)
    text = perform_ocr(image)
    st.image(image, caption="Uploaded Image")
    st.text_area("OCR Result", text, height=200)
    return text

def process_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    images = convert_from_bytes(pdf_bytes)
    all_text = []
    for i, image in enumerate(images):
        processing_status.write(f"Processing page {i+1} of {len(images)}...")
        text = perform_ocr(image)
        all_text.append(text)
        
        # Update the full text
        full_text = "\n\n".join(all_text)
        full_text_placeholder.text_area("Full Text", full_text, height=300)
        
        st.image(image, caption=f"Page {i+1}")
        st.text_area(f"OCR Result - Page {i+1}", text, height=200)
    
    return full_text

def create_epub(text, title="OCR Result"):
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title(title)
    book.set_language('en')

    c1 = epub.EpubHtml(title='Content', file_name='content.xhtml', lang='en')
    c1.content = f'<h1>{title}</h1><p>{text.replace(chr(10), "<br>")}</p>'

    book.add_item(c1)

    book.toc = (epub.Link('content.xhtml', 'Content', 'content'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ['nav', c1]

    return book

if uploaded_file is not None and not st.session_state.file_processed:
    file_type = uploaded_file.type
    processing_status.write(f"Processing {file_type} file...")

    try:
        if file_type == "application/pdf":
            st.session_state.full_text = process_pdf(uploaded_file)
        elif file_type.startswith("image/"):
            st.session_state.full_text = process_image(uploaded_file)
            full_text_placeholder.text_area("Full Text", st.session_state.full_text, height=300)
        else:
            st.error("Unsupported file type")
            st.session_state.full_text = ""

        if st.session_state.full_text:
            processing_status.write("Processing complete ✅")
            st.session_state.file_processed = True

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if st.session_state.file_processed:
    # Create two columns for the download buttons
    col1, col2 = download_buttons_placeholder.columns(2)

    # Display the text download button
    col1.download_button(
        label="Download full text",
        data=st.session_state.full_text,
        file_name="ocr_result.txt",
        mime="text/plain"
    )

    # Create the EPUB file
    epub_book = create_epub(st.session_state.full_text)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as tmp_file:
        epub.write_epub(tmp_file.name, epub_book)
        with open(tmp_file.name, 'rb') as file:
            epub_data = file.read()
        
    # Display the EPUB download button
    col2.download_button(
        label="Download as EPUB",
        data=epub_data,
        file_name="ocr_result.epub",
        mime="application/epub+zip"
    )
    
    os.unlink(tmp_file.name)  # Delete the temporary file

st.write("Note: This tool uses Tesseract for OCR and pdf2image to convert PDFs into images.")
