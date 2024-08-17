import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import os

# Specify the path to your custom tessdata directory
custom_tessdata_dir = os.path.abspath('./custom_tessdata')

st.title("OCR PDFs and images (Bengali and English)")
st.write("This tool runs OCR on PDFs and images, recognizing both Bengali and English text.")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF or image file", type=["pdf", "png", "jpg", "jpeg"])

# Create a placeholder for the full text
full_text_placeholder = st.empty()

# Create a placeholder for the download button
download_button_placeholder = st.empty()

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
        text = perform_ocr(image)
        all_text.append(text)
        
        # Update the full text
        full_text = "\n\n".join(all_text)
        full_text_placeholder.text_area("Full Text", full_text, height=300)
        
        st.image(image, caption=f"Page {i+1}")
        st.text_area(f"OCR Result - Page {i+1}", text, height=200)
    
    return full_text

if uploaded_file is not None:
    file_type = uploaded_file.type
    st.write(f"Processing {file_type} file...")

    try:
        if file_type == "application/pdf":
            full_text = process_pdf(uploaded_file)
        elif file_type.startswith("image/"):
            full_text = process_image(uploaded_file)
            full_text_placeholder.text_area("Full Text", full_text, height=300)
        else:
            st.error("Unsupported file type")
            full_text = ""

        if full_text:
            # Display the download button below the full text box
            download_button_placeholder.download_button(
                label="Download full text",
                data=full_text,
                file_name="ocr_result.txt",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

st.write("Note: This tool uses Tesseract for OCR and pdf2image to convert PDFs into images.")