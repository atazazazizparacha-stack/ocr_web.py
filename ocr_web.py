import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AI Multi-Lingual Scanner", layout="wide")

st.title("🚀 Advanced Urdu, Arabic & English Scanner")
st.write("PDF ya Images se text nikal kar Word mein convert karein.")

# Language Selection
languages = st.multiselect("Zaban select karein:", ["en", "ur", "ar"], default=["en", "ur"])

uploaded_file = st.file_uploader("File select karein (PDF, JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # EasyOCR Reader setup
    @st.cache_resource
    def load_reader(langs):
        return easyocr.Reader(langs)
    
    reader = load_reader(languages)
    full_text = ""
    
    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI scan kar raha hai... is mein thora waqt lag sakta hai."):
            
            # PDF Processing
            if uploaded_file.type == "application/pdf":
                doc_pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page_num in range(len(doc_pdf)):
                    page = doc_pdf.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # High quality
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    st.image(img, caption=f"Page {page_num + 1}", width=400)
                    
                    # OCR on page image
                    result = reader.readtext(np.array(img), detail=0)
                    page_text = "\n".join(result)
                    full_text += f"\n--- Page {page_num + 1} ---\n" + page_text
            
            # Image Processing
            else:
                img = Image.open(uploaded_file)
                st.image(img, width=400)
                result = reader.readtext(np.array(img), detail=0)
                full_text = "\n".join(result)

            st.success("Scanning Mukammal!")
            st.text_area("Scanned Text", full_text, height=300)

            # Word Download Button
            doc = Document()
            doc.add_paragraph(full_text)
            buffer = BytesIO()
            doc.save(buffer)
            st.download_button("📥 Download Scanned Word File", data=buffer.getvalue(), file_name="ai_scan_result.docx")
