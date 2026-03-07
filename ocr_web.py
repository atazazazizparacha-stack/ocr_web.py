import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import fitz
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AI Scanner", layout="wide")
st.title("🚀 AI Scanner (Urdu/Arabic/English)")

# Sidebar Settings
langs = st.sidebar.multiselect("Languages", ["en", "ur", "ar"], default=["en", "ur"])
zoom = st.sidebar.slider("Quality", 1.0, 3.0, 2.0)

up_file = st.file_uploader("Upload File", type=["pdf", "png", "jpg", "jpeg"])

if up_file:
    reader = easyocr.Reader(langs)
    text_result = ""

    if st.button("Start Scanning"):
        with st.spinner("Processing..."):
            try:
                if up_file.type == "application/pdf":
                    pdf = fitz.open(stream=up_file.read(), filetype="pdf")
                    for page in pdf:
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        st.image(img, width=400)
                        res = reader.readtext(np.array(img), detail=0)
                        text_result += "\n".join(res) + "\n\n"
                else:
                    img = Image.open(up_file)
                    st.image(img, width=400)
                    res = reader.readtext(np.array(img), detail=0)
                    text_result = "\n".join(res)

                st.success("Scanning Done!")
                
                # Word File Creation
                doc = Document()
                for line in text_result.split('\n'):
                    if line.strip():
                        p = doc.add_paragraph(line)
                        if any(ord(c) > 1200 for c in line):
                            p.paragraph_format.alignment = 2 # Right
                        else:
                            p.paragraph_format.alignment = 0 # Left

                buf = BytesIO()
                doc.save(buf)
                st.download_button("📥 Download Word", buf.getvalue(), "result.docx")
                st.text_area("Preview", text_result, height=300)

            except Exception as e:
                st.error(f"Error: {e}")
