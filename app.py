import os
import re
import io
import pandas as pd
import streamlit as st
from pypdf import PdfReader
import docx
from pptx import Presentation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page Setup
st.set_page_config(
    page_title="Apna Private Search Engine", 
    page_icon="⚡", 
    layout="wide"
)

# Force Hide Fork, GitHub Icon, Header, and Streamlit Footer
st.markdown("""
    <style>
    /* Streamlit top header completely hide karein */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Top Right Menu Actions (Fork, GitHub, Options) */
    [data-testid="stHeaderActionElements"], 
    .stAppHeader, 
    #MainMenu, 
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Sidebar toggle button ko visible aur accessible rakhein */
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        display: block !important;
        visibility: visible !important;
    }
    </style>
""", unsafe_allow_html=True)

def extract_text_from_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    text_chunks = []

    try:
        if ext in ['.txt', '.md', '.py', '.c', '.cpp', '.java', '.html', '.css', '.js', '.json']:
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            if content.strip():
                text_chunks.append({"page": 1, "text": content})

        elif ext == '.pdf':
            pdf_bytes = io.BytesIO(uploaded_file.read())
            reader = PdfReader(pdf_bytes)
            for page_num, page in enumerate(reader.pages, start=1):
                t = page.extract_text()
                if t and t.strip():
                    text_chunks.append({"page": page_num, "text": t})

        elif ext == '.docx':
            doc = docx.Document(uploaded_file)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            if full_text:
                text_chunks.append({"page": 1, "text": full_text})

        elif ext == '.pptx':
            prs = Presentation(uploaded_file)
            for idx, slide in enumerate(prs.slides, start=1):
                slide_text = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text)
                if slide_text:
                    text_chunks.append({"page": idx, "text": "\n".join(slide_text)})
    except Exception as e:
        st.warning(f"Error reading {uploaded_file.name}: {e}")

    return text_chunks

def highlight_words(text, query):
    clean_query = query.replace('"', '').strip()
    keywords = [re.escape(word) for word in clean_query.split() if len(word) > 1]
    if not keywords:
        return text
    pattern = re.compile(r'(' + '|'.join(keywords) + r')', re.IGNORECASE)
    return pattern.sub(r'<mark style="background-color: #fde047; color: #000; padding: 2px 4px; border-radius: 3px;">\1</mark>', text)

# Header
st.markdown("""
    <h1 style='text-align: left; font-size: 2.8rem; font-weight: 800; background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        ⚡ Apna Private Search Engine
    </h1>
""", unsafe_allow_html=True)
st.caption("On-demand Multi-Format Local Search (PDFs, Word, PPT, & Code Files)")

# Sidebar Uploader
st.sidebar.title("🛠️ Control Panel")
uploaded_files = st.sidebar.file_uploader(
    "📤 Upload Files to Search", 
    type=['pdf', 'docx', 'pptx', 'txt', 'py', 'java', 'c', 'cpp', 'html', 'js'],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("👈 Please upload your PDF, Word, PPT, or Code files from the sidebar to begin searching.")
else:
    # Process Files Dynamic Indexing
    chunk_records = []
    for u_file in uploaded_files:
        chunks = extract_text_from_file(u_file)
        for c in chunks:
            chunk_records.append({
                "file_name": u_file.name,
                "file_type": os.path.splitext(u_file.name)[1].upper().replace('.', ''),
                "page_no": c["page"],
                "text": c["text"],
                "file_bytes": u_file.getvalue()
            })

    if not chunk_records:
        st.error("Uploaded files contained no readable text.")
    else:
        df = pd.DataFrame(chunk_records)
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(df["text"])

        file_types = ["ALL"] + list(df['file_type'].unique())
        selected_type = st.sidebar.selectbox("📁 Filter by File Type:", file_types)
        st.sidebar.metric("Total Extracted Chunks", len(df))

        # Search Bar UI
        col1, col2 = st.columns([5, 1])
        with col1:
            query = st.text_input("Search Query", placeholder="Enter query e.g., Ternary Operators, function, array", label_visibility="collapsed")
        with col2:
            search_btn = st.button("🔍 Search", use_container_width=True)

        if query or search_btn:
            clean_query = query.replace('"', '').strip()
            if clean_query:
                query_vec = vectorizer.transform([clean_query])
                similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()

                df["score"] = similarity
                results_df = df[df["score"] > 0.05].copy()

                if len(clean_query.split()) > 1:
                    words = clean_query.lower().split()
                    results_df = results_df[results_df['text'].apply(lambda t: all(w in t.lower() for w in words))]

                results_df = results_df.sort_values(by="score", ascending=False)

                if selected_type != "ALL":
                    results_df = results_df[results_df['file_type'] == selected_type]

                st.subheader(f"Matching Results ({len(results_df)} matches found)")

                if results_df.empty:
                    st.info("No relevant matches found for your query.")
                else:
                    for _, row in results_df.head(15).iterrows():
                        score_pct = round(float(row['score']) * 100, 1)
                        file_badge = f"[{row['file_type']}]"
                        highlighted_text = highlight_words(row["text"].strip()[:1500], query)
                        
                        with st.expander(f"📄 {file_badge} {row['file_name']} (Page/Slide {row['page_no']}) — Relevance: {score_pct}%"):
                            st.markdown(highlighted_text, unsafe_allow_html=True)
                            st.markdown("---")
                            st.download_button(
                                label=f"📥 Download {row['file_name']}",
                                data=row['file_bytes'],
                                file_name=row['file_name'],
                                mime="application/octet-stream",
                                key=f"dl_{row['file_name']}_{row['page_no']}"
                            )