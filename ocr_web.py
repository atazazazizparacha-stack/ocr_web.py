import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Pt
import pandas as pd
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="AI Multi-Lingual Pro Scanner", layout="wide")

st.title("🚀 Smart AI Scanner (Urdu, Arabic & English)")
st.write("PDF/Images ko scan karein. Word file ab RTL support ke saath generate hogi.")

# Sidebar Settings
with st.sidebar:
    st.header("Settings")
    languages = st.multiselect("Zaban select karein:", ["en", "ur", "ar"], default=["en", "ur"])
    zoom = st.slider("Scan Quality (Higher is better)", 1.0, 4.0, 2.5)

uploaded_file = st.file_uploader("File select karein", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    @st.cache_resource
    def load_reader(langs):
        return easyocr.Reader(langs)
    
    reader = load_reader(languages)
    full_text = ""

    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI scan kar raha hai..."):
            if uploaded_file.type == "application/pdf":
                doc_pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page_num in range(len(doc_pdf)):
                    page = doc_pdf.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    st.image(img, caption=f"Page {page_num + 1}", width=400)
                    
                    result = reader.readtext(np.array(img), detail=0)
                    full_text += "\n".join(result) + "\n\n"
            else:
                img = Image.open(uploaded_file)
                st.image(img, width=400)
                result = reader.readtext(np.array(img), detail=0)
                full_text = "\n".join(result)

            st.success("Scanning Mukammal!")

            # --- WORD FILE GENERATION ---
            doc = Document()
            # Font setting for better Urdu/Arabic display
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(12)

            # Text ko paragraphs mein split karke add karna
            for line in full_text.split('\n'):
                if line.strip():
                    p = doc.add_paragraph(line)
                    # Simple check for RTL: Agar line mein koi Urdu/Arabic character hai
                    if any(ord(c) > 1200 for c in line):
                        p.paragraph_format.alignment = 2 # 2 ka matlab hai RIGHT alignment
                    else:
                        p.paragraph_format.alignment = 0 # 0 ka matlab hai LEFT alignment

            word_buf = BytesIO()
            doc.save(word_buf)
            
            st.download_button("📥 Download Scanned Word File", data=word_buf.getvalue(), file_name="ai_scanner_result.docx")
            st.text_area("Live Preview", full_text, height=300)
