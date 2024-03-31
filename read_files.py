# -*- coding: utf-8 -*-

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document

def read_pdf(file):
    reader = PdfReader(file)
    pages = reader.pages
    text = ""
    for page in pages:
        sub = page.extract_text()
        text += sub
    return text

def read_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def save_txt(sts):
    result = ""
    for key in sts.keys():
        result += f"{key}: {sts[key]}\n"
    return result