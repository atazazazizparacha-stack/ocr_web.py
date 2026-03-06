import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import pandas as pd
from docx import Document
from io import BytesIO
import pdfplumber

st.set_page_config(page_title="AI Multi-Tool Scanner", layout="wide")

st.title("🚀 All-in-One AI Scanner & Converter")
st.write("Images (OCR) aur PDF files ko Word/Excel mein convert karein.")

# 1. Selection Mode
mode = st.radio("Kya process karna chahte hain?", ["📷 Image to Text (OCR)", "📄 PDF to Word/Excel"])

# --- MODE 1: IMAGE TO TEXT ---
if mode == "📷 Image to Text (OCR)":
    languages = st.multiselect("Zaban select karein:", ["en", "ur", "ar"], default=["en"])
    uploaded_images = st.file_uploader("Photos select karein...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

    if uploaded_images:
        reader = easyocr.Reader(languages)
        all_text = ""
        
        for img_file in uploaded_images:
            img = Image.open(img_file)
            st.image(img, caption=img_file.name, width=300)
            
            if st.button(f"Scan {img_file.name}"):
                with st.spinner("AI parh raha hai..."):
                    result = reader.readtext(np.array(img), detail=0)
                    text = "\n".join(result)
                    st.text_area(f"Result: {img_file.name}", text, height=150)
                    all_text += f"\n--- {img_file.name} ---\n" + text

        if all_text:
            # Word Download
            doc = Document()
            doc.add_paragraph(all_text)
            buffer = BytesIO()
            doc.save(buffer)
            st.download_button("📥 Download all as Word", data=buffer.getvalue(), file_name="scanned_images.docx")

# --- MODE 2: PDF TO WORD/EXCEL ---
elif mode == "📄 PDF to Word/Excel":
    uploaded_pdf = st.file_uploader("PDF file upload karein...", type=["pdf"])
    
    if uploaded_pdf:
        with pdfplumber.open(uploaded_pdf) as pdf:
            full_text = ""
            table_data = []
            
            with st.spinner("PDF process ho rahi hai..."):
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                    # Excel ke liye tables nikalna
                    tables = page.extract_tables()
                    for table in tables:
                        table_data.extend(table)

            st.success("PDF ki processing mukammal!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Word Converter")
                doc = Document()
                doc.add_paragraph(full_text)
                word_buf = BytesIO()
                doc.save(word_buf)
                st.download_button("📥 Download as Word", data=word_buf.getvalue(), file_name="pdf_to_word.docx")
            
            with col2:
                st.subheader("Excel Converter")
                if table_data:
                    df = pd.DataFrame(table_data)
                    excel_buf = BytesIO()
                    df.to_excel(excel_buf, index=False, header=False)
                    st.download_button("📥 Download Tables as Excel", data=excel_buf.getvalue(), file_name="pdf_tables.xlsx")
                else:
                    st.warning("PDF mein koi table nahi mila.")
