import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

# Basic Page Setup
st.set_page_config(page_title="AI Scanner Pro", layout="wide")

st.title("🚀 Smart AI Scanner")
st.write("PDF/Images scan karein aur Word file download karein.")

# Settings Sidebar
with st.sidebar:
    st.header("Settings")
    langs = st.multiselect("Zaban (Languages):", ["en", "ur", "ar"], default=["en", "ur"])
    zoom_val = st.slider("Quality", 1.0, 3.0, 2.0)

uploaded_file = st.file_uploader("File select karein", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # OCR Reader Load karna
    @st.cache_resource
    def get_reader(l):
        return easyocr.Reader(l)
    
    reader = get_reader(langs)
    full_text = ""

    if st.button("Scan Shuru Karein"):
        with st.spinner("AI processing ho rahi hai..."):
            try:
                # PDF Processing
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    for page in doc:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_val, zoom_val))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        st.image(img, width=400)
                        
                        result = reader.readtext(np.array(img), detail=0)
                        full_text += "\n".join(result) + "\n\n"
                
                # Image Processing
                else:
                    img = Image.open(uploaded_file)
                    st.image(img, width=400)
                    result = reader.readtext(np.array(img), detail=0)
                    full_text = "\n".join(result)

                st.success("Scan Mukammal!")

                # Create Word File
                word_doc = Document()
                for line in full_text.split('\n'):
                    if line.strip():
                        p = word_doc.add_paragraph(line)
                        # Urdu/Arabic ke liye Right Align (Simple Method)
                        if any(ord(c) > 1200 for c in line):
                            p.paragraph_format.alignment = 2 
                        else:
                            p.paragraph_format.alignment = 0

                # Download Button
                buf = BytesIO()
                word_doc.save(buf)
                st.download_button("📥 Download Word File", buf.getvalue(), "scanned_result.docx")
                st.text_area("Preview", full_text, height=300)

            except Exception as e:
                st.error(f"Ek masla aaya hai: {e}")
