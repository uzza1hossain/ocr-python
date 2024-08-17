import streamlit as st
import os
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import base64

# Set page title
st.set_page_config(page_title="OCR PDFs and images")

st.title("OCR PDFs and images")
st.write("This tool runs OCR on PDFs and images.")

# Language selection
# LANGUAGES = {
#     "eng": "English",
#     "ben": "Bengali",
#     "fra": "French",
#     "deu": "German",
#     "spa": "Spanish",
#     # Add more languages as needed
# }

# selected_language = st.selectbox("Select language", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])
selected_language = "ben+eng"

# File uploader
uploaded_file = st.file_uploader("Choose a PDF or image file", type=["pdf", "png", "jpg", "jpeg"])
custom_tessdata_dir = os.path.abspath('./custom_tessdata')
def perform_ocr(image, language='eng'):
    return pytesseract.image_to_string(image, lang=language, config=f'--tessdata-dir "{custom_tessdata_dir}"')

# def process_pdf(pdf_file, language='eng'):
#     pdf_bytes = pdf_file.read()
#     images = convert_from_path(io.BytesIO(pdf_bytes))
#     all_text = []
#     for i, image in enumerate(images):
#         text = perform_ocr(image, language)
#         all_text.append(text)
#         st.image(image, caption=f"Page {i+1}")
#         st.text_area(f"OCR Result - Page {i+1}", text, height=200)
#     return "\n\n".join(all_text)
def process_pdf(pdf_file, language='eng'):
    pdf_bytes = pdf_file.read()
    images = convert_from_bytes(pdf_bytes)
    all_text = []
    for i, image in enumerate(images):
        text = perform_ocr(image, language)
        all_text.append(text)
        st.image(image, caption=f"Page {i+1}")
        st.text_area(f"OCR Result - Page {i+1}", text, height=200)
    return "\n\n".join(all_text)

def process_image(image_file, language='eng'):
    image = Image.open(image_file)
    text = perform_ocr(image, language)
    st.image(image, caption="Uploaded Image")
    st.text_area("OCR Result", text, height=200)
    return text

if uploaded_file is not None:
    file_type = uploaded_file.type
    st.write(f"Processing {file_type} file...")

    try:
        if file_type == "application/pdf":
            full_text = process_pdf(uploaded_file, selected_language)
        elif file_type.startswith("image/"):
            full_text = process_image(uploaded_file, selected_language)
        else:
            st.error("Unsupported file type")
            full_text = ""

        if full_text:
            st.download_button(
                label="Download full text",
                data=full_text,
                file_name="ocr_result.txt",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

st.write("Note: This tool uses Tesseract for OCR and pdf2image to convert PDFs into images.")
