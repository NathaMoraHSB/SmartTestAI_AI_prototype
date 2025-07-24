import os
import time
import requests
from bs4 import BeautifulSoup

import traceback
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import urljoin, urlparse

import lancedb

from openai import OpenAI
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

from infrastructure.gpt.files_intake.utils.tokenizer import OpenAITokenizerWrapper
from infrastructure.gpt.configs.assistant_env_config import API_KEY, API_URL
from infrastructure.gpt.files_intake.utils.sitemap import get_sitemap_urls

#------------------Initialization & Setup---------------------------------------------------

# Initialize tokenizer for controlling token limits during chunking
tokenizer = OpenAITokenizerWrapper()
# Initialize OpenAI client
client = OpenAI()
# Retrieve the OpenAI embedding function class from LanceDB registry
embedding_func_cls = get_registry().get("openai")
# Initialize document converter (handles PDF, DOCX, spreadsheets, webpages, etc.)
converter = DocumentConverter()


# Select and initialize the embedding model
# Available models:
#   - "text-embedding-3-small" → fast, lightweight, 1536 dimensions
#   - "text-embedding-3-large" → better semantic performance, 3072 dimensions

embedding_func = embedding_func_cls.create(name="text-embedding-3-large")


#------------------Project Base Path and LanceDB Connection-----------------------------------

# Set project root directory (go 2 levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[2]

# Define the path for the LanceDB vector database
DB_PATH = BASE_DIR / "lancedb"

# Connect or create LanceDB, this located the db in our project
db = lancedb.connect(str(DB_PATH))

#------------------LanceDB Schema Definitions---------------------------------------------------------

# Define metadata structure for each document chunk
class ChunkMetadata(LanceModel):
    filename: str | None
    project_id: str | None
    file_type: str | None
    description: str | None
    upload_date: str | None

# Define LanceDB vector record structure
class ChunkRecord(LanceModel):
    text: str = embedding_func.SourceField()
    vector: Vector(embedding_func.ndims()) = embedding_func.VectorField()
    metadata: ChunkMetadata

#------------------Metadata Construction---------------------------------------------------------

# Generate metadata for an uploaded file
def build_file_metadata(file_name: str, project_id: str, file_type: str, description: str) -> dict:
    return {
        "filename": file_name,
        "project_id": project_id,
        "file_type": file_type,
        "description": description,
        "upload_date": datetime.now().isoformat()
    }

#------------------Store Chunks in LanceDB-------------------------------------------------------------------------

# Save chunked content with vector embeddings to LanceDB
def store_chunks_in_lancedb(chunks: List, meta_info: dict, table_name: str = "files"):
    print("\n💾 Saving chunks to LanceDB...")

    # Reuse existing table or create a new one
    if table_name in db.table_names():
        table = db.open_table(table_name)
    else:
        table = db.create_table(table_name, schema=ChunkRecord)

    records = []

    # Convert each chunk into a LanceDB record
    for i, chunk in enumerate(chunks):
        try:
            if isinstance(chunk, dict) and "text" in chunk:
                # Fallback para CSV/Excel
                text = chunk["text"]
                filename = meta_info.get("filename", "unknown")
            elif hasattr(chunk, "text") and hasattr(chunk, "meta"):
                # DOCX, PDF, etc.
                text = chunk.text
                filename = chunk.meta.origin.filename
            else:
                print(f"⚠️ Chunk {i+1} is invalid or unsupported type. Skipping.")
                continue

            record = {
                "text": text,
                "metadata": {
                    "filename": filename,
                    "project_id": meta_info.get("project_id"),
                    "file_type": meta_info.get("file_type"),
                    "description": meta_info.get("description"),
                    "upload_date": meta_info.get("upload_date")
                },
            }
            records.append(record)

        except Exception as e:
            print(f"⚠️ Error processing chunk {i+1}: {e}")

    # Store all valid records
    if records:
        table.add(records)
        print(f"✅ {len(records)} chunks saved with embeddings.")
    else:
        print("⚠️ No valid records to save.")

#------------------Duplicate Check-----------------------------------------------------------------------------------

# Check if a file with the same filename and project ID already exists in the database
def is_duplicate(meta_info: dict, table_name: str = "files") -> bool:
    if table_name not in db.table_names():
        return False

    table = db.open_table(table_name)
    filename = meta_info.get("filename", "").lower().strip()
    project_id = meta_info.get("project_id", "")

    results = table.to_pandas()
    for _, row in results.iterrows():
        md = row.get("metadata", {})
        if not md:
            continue

        if (
                md.get("filename", "").lower().strip() == filename and
                md.get("project_id", "") == project_id
        ):
            return True

    return False

#------------------File Processing Functions (PDF, DOCX)----------------------------------------------------------

# Convert and store a single PDF file into chunks
def process_single_pdf(pdf_path: str, project_id: str, file_type: str, description: str, table_name: str = "files"):
    """
    Process a single PDF file: convert, chunk, check for duplicates, and store in LanceDB.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    converter = DocumentConverter()
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=8191, merge_peers=True)

    result = converter.convert(pdf_path)
    if not result or not result.document:
        print("❌ Failed to convert PDF document.")
        return

    meta_info = build_file_metadata(
        file_name=os.path.basename(pdf_path),
        project_id=project_id,
        file_type=file_type,
        description=description
    )

    if is_duplicate(meta_info, table_name):
        print("⚠️ File already indexed. Skipping.")
    else:
        chunks = list(chunker.chunk(dl_doc=result.document))
        print(f"✅ {len(chunks)} chunks created.")
        store_chunks_in_lancedb(chunks, meta_info, table_name)

# Convert and store a single DOCX file into chunks
def process_single_docx(docx_path: str, project_id: str, file_type: str, description: str, table_name: str = "files"):
    """
    Process a single DOCX file: convert, chunk, check for duplicates, and store in LanceDB.
    """
    if not os.path.exists(docx_path):
        print(f"❌ File not found: {docx_path}")
        return

    converter = DocumentConverter()
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=8191, merge_peers=True)

    result = converter.convert(docx_path)
    if not result or not result.document:
        print("❌ Failed to convert DOCX document.")
        return

    document = result.document
    chunks = list(chunker.chunk(dl_doc=document))

    meta_info = build_file_metadata(
        file_name=os.path.basename(docx_path),
        project_id=project_id,
        file_type=file_type,
        description=description
    )

    if is_duplicate(meta_info, table_name):
        print("⚠️ File already indexed. Skipping.")
    else:
        print(f"✅ Number of chunks: {len(chunks)}")
        store_chunks_in_lancedb(chunks, meta_info, table_name)

#------------Spreadsheet Processing (CSV, XLSX)-------------------------------------------------------------------

# Create text chunks from each row of a markdown table (used for spreadsheets)
def chunk_table_by_rows(document, max_chunks: int = 100) -> List[dict]:
    """
    Fallback chunking for table-like documents: return one chunk per row as plain text.
    """
    table_md = document.export_to_markdown()
    lines = table_md.strip().splitlines()

    # Skip header and divider lines if present
    content_lines = [line for line in lines if line.strip().startswith("|") and "---" not in line]
    header = content_lines[0] if content_lines else ""

    chunks = []
    for i, line in enumerate(content_lines[1:max_chunks]):
        chunk_text = f"{header}\n{line}"
        chunks.append({"text": chunk_text})

    return chunks

# Convert and store a spreadsheet file (CSV or XLSX) into chunks
def process_single_spreadsheet(file_path: str, project_id: str, file_type: str, description: str, table_name: str = "files"):
    """
    Process a single spreadsheet file (Excel or CSV): convert, chunk, check for duplicates, and store in LanceDB.
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    if not (file_path.endswith(".csv") or file_path.endswith(".xlsx")):
        print("⚠️ Only .csv and .xlsx files are supported for spreadsheet processing.")
        return

    converter = DocumentConverter()
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=8191, merge_peers=True)

    result = converter.convert(file_path)
    if not result or not result.document:
        print("❌ Failed to convert spreadsheet.")
        return

    document = result.document
    exported = document.export_to_markdown()

    if not isinstance(exported, str) or not exported.strip():
        print("❌ Converted content is empty or invalid for tokenization.")
        return

    try:
        chunks = chunk_table_by_rows(document)
    except Exception as e:
        print(f"❌ Error during chunking: {e}")
        print("🔎 Content preview:")
        print(exported[:1000])
        return

    meta_info = build_file_metadata(
        file_name=os.path.basename(file_path),
        project_id=project_id,
        file_type=file_type,
        description=description
    )

    if is_duplicate(meta_info, table_name):
        print("⚠️ File already indexed. Skipping.")
    else:
        print(f"✅ Number of chunks: {len(chunks)}")
        store_chunks_in_lancedb(chunks, meta_info, table_name)

#----------------------------------Folder Batch Processing--------------------------------------------------------

# Process all supported files in a given folder (PDF, DOCX, XLSX, CSV)
def process_all_supported_files_in_folder(
        folder_path: str,
        project_id: str,
        description: str,
        table_name: str = "files"
):

    print("\n📁 Starting general processing of supported files in folder...\n")

    supported_extensions = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".xlsx": "excel",
        ".csv": "csv"
    }

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1].lower()

        file_type = supported_extensions.get(ext)
        if not file_type:
            print(f"⚠️ Unsupported file type: {filename}")
            continue

        print(f"\n➡️ Processing `{filename}` as `{file_type}`")

        if file_type == "pdf":
            process_single_pdf(
                pdf_path=file_path,
                project_id=project_id,
                file_type=file_type,
                description=description,
                table_name=table_name
            )
        elif file_type == "docx":
            process_single_docx(
                docx_path=file_path,
                project_id=project_id,
                file_type=file_type,
                description=description,
                table_name=table_name
            )
        elif file_type in {"excel", "csv"}:
            process_single_spreadsheet(
                file_path=file_path,
                project_id=project_id,
                file_type=file_type,
                description=description,
                table_name=table_name
            )
    print("\n✅ Folder processing complete.\n")

#----------------------Website Processing (Web Pages & Sitemaps)--------------------------------------------------

# Convert and store content from a single web page (HTML/XML)
def process_single_webpage(url: str, project_id: str, description: str, table_name: str = "files"):
    """
    Process a single webpage (HTML or XML if it renders page-like content).
    """
    try:
        print(f"\n🌐 Processing single webpage: {url}")
        converter = DocumentConverter()
        chunker = HybridChunker(tokenizer=tokenizer, max_tokens=8191, merge_peers=True)

        result = converter.convert(url)
        if not result or not result.document:
            print("❌ Could not convert the web page content.")
            return

        chunks = list(chunker.chunk(dl_doc=result.document))
        meta_info = build_file_metadata(
            file_name=url,
            project_id=project_id,
            file_type="webpage",
            description=description
        )

        if is_duplicate(meta_info, table_name):
            print("⚠️ Page already indexed. Skipping.")
        else:
            print(f"✅ {len(chunks)} chunks created.")
            store_chunks_in_lancedb(chunks, meta_info, table_name)

    except Exception as e:
        print(f"❌ Error processing single web page: {e}")

# Extract and process multiple pages from a sitemap
def process_sitemap_html(base_url: str, project_id: str, description: str, table_name: str = "files"):
    print(f"\n🗺️ Processing sitemap: {base_url}")
    try:
        sitemap_urls = get_sitemap_urls(base_url)
        if not sitemap_urls or len(sitemap_urls) == 1:
            raise ValueError("Sitemap appears empty or insufficient.")

        converter = DocumentConverter()
        chunker = HybridChunker(tokenizer=tokenizer, max_tokens=8191, merge_peers=True)

        conv_results_iter = converter.convert_all(sitemap_urls)
        total_chunks = 0

        for i, result in enumerate(conv_results_iter):
            if not result or not result.document:
                print(f"❌ Conversion failed for: {sitemap_urls[i]}")
                continue

            document = result.document
            chunks = list(chunker.chunk(dl_doc=document))

            meta_info = build_file_metadata(
                file_name="file",
                project_id=project_id,
                file_type="webpage",
                description=description
            )

            print(f"✅ {len(chunks)} chunks from: {sitemap_urls[i]}")
            store_chunks_in_lancedb(chunks, meta_info, table_name)
            total_chunks += len(chunks)

        if total_chunks == 0:
            raise ValueError("No chunks created from sitemap pages.")

        print(f"\n🌐 Sitemap processed successfully. Total chunks: {total_chunks}")

    except Exception as e:
        raise RuntimeError(f"Failed to process sitemap: {e}")

# Crawl a website to collect internal links up to a limit
def extract_internal_links(base_url, max_links=20):
    visited = set()
    to_visit = [base_url]
    all_links = []

    while to_visit and len(all_links) < max_links:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            all_links.append(url)

            for link_tag in soup.find_all("a", href=True):
                href = link_tag["href"]
                full_url = urljoin(url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)
        except Exception as e:
            print(f"⚠️ Skipped {url} due to error: {e}")

    return all_links

# Process all internal pages from a website via crawling
def crawl_and_process_site(start_url: str, project_id: str, description: str, table_name: str = "files", max_links: int = 20):
    print(f"\n🌐 Crawling and processing site: {start_url}")
    links = extract_internal_links(start_url, max_links=max_links)
    print(f"🔗 Found {len(links)} internal pages to process.")

    converter = DocumentConverter()
    chunker = HybridChunker(tokenizer=tokenizer, max_tokens=8191, merge_peers=True)

    results = converter.convert_all(links)
    total_chunks = 0

    for result, url in zip(results, links):
        if not result or not result.document:
            print(f"❌ Failed to process {url}")
            continue

        chunks = list(chunker.chunk(dl_doc=result.document))
        print(f"✅ {len(chunks)} chunks from: {url}")

        meta = build_file_metadata(
            file_name=url,
            project_id=project_id,
            file_type="webpage",
            description=description
        )

        if is_duplicate(meta, table_name):
            print(f"⚠️ Skipped duplicate: {url}")
            continue

        store_chunks_in_lancedb(chunks, meta, table_name)
        total_chunks += len(chunks)

    print(f"\n🎯 Done! Total chunks stored: {total_chunks}")

# Automatically choose the best method (sitemap or crawler) to process an entire website
def process_entire_website(url: str, project_id: str, description: str, table_name: str = "files", max_links: int = 20):
    print(f"\n🔍 Analyzing best method for: {url}")

    try:
        sitemap_urls = get_sitemap_urls(url)
        if sitemap_urls and all(urlparse(link).scheme in ["http", "https"] for link in sitemap_urls):
            print("📡 Sitemap found. Using sitemap-based extraction...")
            process_sitemap_html(
                base_url=url,
                project_id=project_id,
                description=description,
                table_name=table_name
            )
        else:
            raise ValueError("Sitemap invalid or unusable")

    except Exception as e:
        print(f"⚠️ Falling back to crawler due to sitemap error: {e}")
        crawl_and_process_site(
            start_url=url,
            project_id=project_id,
            description=description,
            table_name=table_name,
            max_links=max_links
        )