# ⚡ Apna Private Search Engine

An enterprise-grade, privacy-focused local search and document retrieval system built using Python and Streamlit. This application indexes documents locally or via web UI, enabling fast, keyword-accurate searches across multiple file formats without sending data to external APIs.

---

## 📌 Project Overview
**Apna Private Search Engine** parses, indexes, and retrieves text from heterogeneous document formats including PDFs, Word documents, PowerPoint presentations, text files, and source code files. It features real-time search, multi-word exact matching, snippet highlighting, dynamic file uploading, and direct file downloads.

---

## 🔑 Key Features

- **Multi-Format Parsing:** Support for `.pdf`, `.docx`, `.pptx`, `.txt`, and code extensions (`.py`, `.js`, `.java`, `.c`, `.cpp`, `.html`, `.css`).
- **Strict Phrase Filtering:** Validates multi-word queries to eliminate irrelevant page matches.
- **Real-Time Highlighting:** Highlights search keywords inside text snippets using custom HTML tags.
- **Dynamic File Uploader:** Drag-and-drop support in the sidebar for uploading new documents directly into the indexing directory.
- **FileType Filtering System:** Filter search queries by specific file formats (e.g., PDF, DOCX, Code).
- **Direct File Downloads:** One-click download button within each search result expander card.

---

## 🛠️ Tech Stack

| Component | Library / Framework | Description |
| :--- | :--- | :--- |
| **Frontend UI** | `streamlit` | Interactive web dashboard & widgets |
| **PDF Extraction** | `pypdf` | Reads and parses text page-by-page |
| **Word Parsing** | `python-docx` | Extracts paragraph content from `.docx` |
| **PPT Parsing** | `python-pptx` | Extracts text frames from `.pptx` slides |
| **Machine Learning** | `scikit-learn` | TF-IDF Vectorization & Cosine Similarity scoring |
| **Data Processing** | `pandas` | Structures document chunks and scoring matrices |

---

## ⚙️ Architecture & Pipeline

```text
[ Raw Documents ] ➔ [ Text Parsing & Chunking ] ➔ [ TF-IDF Vectorization ] ➔ [ Cosine Similarity ] ➔ [ Streamlit Web UI ]