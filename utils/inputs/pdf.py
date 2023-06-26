from functools import cache
from pathlib import Path
from typing import IO, List

from icecream import ic
from langchain.schema import Document
from pypdf import PdfReader


def extract(*pdf_docs: str | IO | Path | List[Document]) -> str:
    text = ''
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()

    ic('extracted pdfs')

    return text
