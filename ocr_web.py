import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
from docx import Document
from io import BytesIO

st.set_page_config(page_title="AI Pro Scanner", layout="wide")

st.title("🚀 Advanced AI PDF & Image Scanner")
st.write("Urdu, Arabic aur English PDF/Images ko Word mein convert karein.")

# Language selection (Urdu aur Arabic support ke liye)
languages = st.multiselect("Zaban select karein (Languages):", ["en", "ur", "ar"], default=["en", "ur"])

uploaded_file = st.file_uploader("File select karein (PDF, JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    reader = easyocr.Reader(languages)
    full_text = ""
    
    if st.button("Scanning Shuru Karein"):
        with st.spinner("AI parh raha hai... is mein thora waqt lag sakta hai."):
            
            # Agar PDF hai to har page ko image bana kar scan karo
            if uploaded_file.type == "application/pdf":
                images = convert_from_bytes(uploaded_file.read())
                for i, page_img in enumerate(images):
                    st.image(page_img, caption=f"Page {i+1}", width=300)
                    result = reader.readtext(np.array(page_img), detail=0)
                    full_text += f"\n--- Page {i+1} ---\n" + "\n".join(result)
            
            # Agar Image hai
            else:
                img = Image.open(uploaded_file)
                st.image(img, width=300)
                result = reader.readtext(np.array(img), detail=0)
                full_text = "\n".join(result)

            st.subheader("Result:")
            st.text_area("Scanned Text", full_text, height=300)

            # Word File Download
            doc = Document()
            # Urdu/Arabic ke liye right-to-left alignment zaroori hai
            p = doc.add_paragraph(full_text)
            
            buffer = BytesIO()
            doc.save(buffer)
            st.download_button("📥 Download Word File", data=buffer.getvalue(), file_name="ai_scan_result.docx")
