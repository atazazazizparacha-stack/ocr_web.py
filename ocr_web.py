import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz
from docx import Document
from io import BytesIO

# --- Simple Setup ---
st.set_page_config(page_title="AI Scanner", layout="wide")
st.title("🚀 Smart AI Scanner")

# --- Sidebar ---
with st.sidebar:
    langs = st.multiselect("Languages:", ["en", "ur", "ar"], default=["en", "ur"])
    zoom = st.slider("Quality:", 1.0, 3.0, 2.0)

up_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

if up_file:
    @st.cache_resource
    def load_model(l):
        return easyocr.Reader(l)
    
    reader = load_model(langs)
    text_data = ""

    if st.button("Start Scan"):
        with st.spinner("Processing..."):
            try:
                # PDF to Image and Scan
                if up_file.type == "application/pdf":
                    pdf_data = fitz.open(stream=up_file.read(), filetype="pdf")
                    for page in pdf_data:
                        m = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=m)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        st.image(img, width=400)
                        res = reader.readtext(np.array(img), detail=0)
                        text_data += "\n".join(res) + "\n\n"
                # Direct Image Scan
                else:
                    img = Image.open(up_file)
                    st.image(img, width=400)
                    res = reader.readtext(np.array(img), detail=0)
                    text_data = "\n".join(res)

                st.success("Done!")

                # --- Create Word File ---
                doc = Document()
                for line in text_data.split('\n'):
                    if line.strip():
                        p = doc.add_paragraph(line)
                        # Right Align for Urdu/Arabic
                        if any(ord(c) > 1200 for c in line):
                            p.paragraph_format.alignment = 2
                        else:
                            p.paragraph_format.alignment = 0

                buf = BytesIO()
                doc.save(buf)
                st.download_button("📥 Download Word", buf.getvalue(), "scan.docx")
                st.text_area("Preview", text_data, height=300)

            except Exception as e:
                st.error(f"Error: {e}")
