from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import (MarkdownHeaderTextSplitter,
                                      RecursiveCharacterTextSplitter)

from src.sources.models import Source

headers_to_split_on = [
    ("-------------------------", "Separator"),
    ("#", "Header 1"),
    # ("##", "Header 2"),
    # ("###", "Header 3"),
]

chunk_size = 600
chunk_overlap = 50


def md2Documents(content) -> List[Document]:
    # Split on Markdown headers
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on, strip_headers=False
    )

    md_header_splits = markdown_splitter.split_text(content)
    # Char-level splits
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    # Split
    return text_splitter.split_documents(md_header_splits)


def source2Documents(source: Source) -> List[Document]:
    docs = []
    for i, d in enumerate(md2Documents(source.content)):
        metadata = source.meta
        metadata["chunk_id"] = i

        docs.append(Document(page_content=d.page_content, metadata=metadata))

    return docs
