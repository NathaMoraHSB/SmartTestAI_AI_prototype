# 🧠 GPT Assistant System – Multi-Assistant Test GUI (Tkinter + OpenAI + LanceDB)

This project provides a modular, extendable assistant system using OpenAI’s **Responses API**, tailored for **software testing workflows**. It integrates a **Tkinter-based desktop interface** with vector context support through **LanceDB**, allowing users to process documents, extract contextual information, and interact with four assistant types:

- **Exploratory Testing Assistant**
- **Interview Preparation Assistant**
- **Summarizing Assistant**
- **Test Results Table Assistant**

---

## 🔧 Architecture Overview

```
gpt/
│
├── configs/              # Assistant definitions & API configuration
├── context/              # Developer context builder for each assistant
├── files_intake/         # File & website processing + chunking + vector DB
├── models/               # Enum for assistant names
├── repositories/         # Core assistant logic and request builder
├── test_data/            # GUI, fake test input and report examples
```

---

## 🧩 Assistant Configuration

Each assistant is defined via `AssistantConfig`:

```python
class AssistantConfig:
    def __init__(self, system, output_format, requires_vector_context=False)
```

Configurations include:
- A **system prompt** to guide the assistant behavior.
- An **output schema** (JSON Schema format) for strict structure enforcement.
- A flag to determine if **vector-based context** is required.

🗂 Defined in:  
- `exploratory_testing_config.py`  
- `interview_questions_config.py`  
- `summarizing_assistant_config.py`  
- `results_table_config.py`

Registered globally via `assistant_registry.py`.

---

## 🧠 Assistant Behavior Summary

| Assistant                | Context Source                 | Uses LanceDB | Output Format                     |
|-------------------------|-------------------------------|--------------|-----------------------------------|
| Exploratory Testing      | Project metadata & goals       | ✅            | JSON → procedure, ideas, notes     |
| Interview Preparation    | Predefined test plan           | ✅            | JSON → questions, purpose, notes   |
| Summarizing              | Developer report               | ❌            | JSON → summary, execution time     |
| Test Results             | Developer report               | ❌            | JSON → table with findings         |

---

## 🗃️ Context Management

Developer context is dynamically generated based on the selected assistant (`developer_context()` in `repositories/assistant_gpt_repository.py`), then added as a system input to the payload.

For assistants needing vector context (e.g., Exploratory Testing), the system uses **LanceDB** to search and include relevant content from uploaded files/websites.

---

## 🧾 Responses API Request Workflow

1. **Assistant selected** (Tkinter GUI).
2. **Prompt entered** + optional images attached.
3. **Vector context** retrieved (if enabled).
4. **Structured payload** generated with:
   - System prompt
   - Developer context
   - User input
5. **Request sent** to OpenAI `/v1/responses` endpoint.
6. **Structured response** is parsed and displayed.

---

## 📦 File & Web Context Intake

The assistant system uses the **Docling** library + **HybridChunker** to convert documents into indexed text chunks with embeddings stored in **LanceDB**.

### ✅ Supported Inputs
- **PDFs** – `process_single_pdf`
- **DOCX** – `process_single_docx`
- **CSV/XLSX** – `process_single_spreadsheet`
- **Websites** – `process_single_webpage` or crawl entire domain via sitemap

### 🧠 Vector Storage
- Chunks are stored in `lancedb/` using a schema (`ChunkRecord`) with metadata including:
  - filename
  - project_id
  - file_type
  - description
  - upload_date

---

## 🖼️ Image Attachment Support

Users can optionally upload images (e.g., screenshots) via the GUI. These are Base64-encoded and embedded into the prompt payload for visual context when needed.

---

## 🧪 Test GUI (Tkinter)

Located in `test_data/gui.py`, the interface allows:

- Selecting an assistant type (radio buttons).
- Entering a prompt.
- Uploading supported files.
- Attaching images.
- Submitting a website (entire or single page).
- Viewing the formatted assistant response.

```bash
# Launch the GUI
python test_data/main_for_testing.py
```

---

## 🔐 Environment Variables

The `.env` file should include:

```
OPENAI_API_KEY=your-api-key
```

Preloaded in `assistant_env_config.py`, this config also disables TF oneDNN warnings and HuggingFace symlinks.

---

## 📁 Example Test Input (folder to delete after integration)

The file `test_data.py` provides realistic example data used for testing assistant behavior:

- Full exploratory test plan
- Pre-filled test report
- Project metadata
- Session descriptions

This data is used in developer context generation for rapid testing and **must** be replaced for the variables in our system.

---

##  Calling of methods in the GUI

The Tkinter GUI is not responsible for doing any heavy lifting. Instead, it:

1. Collects user input (text, files, images, URLs).
2. Calls backend functions that handle processing.
3. Displays the formatted assistant response.

We must replicate this communication logic in Angular, replacing direct function calls with **HTTP requests** to your backend API.

---

## 🧭 Internal Method Flow (Tkinter Side)

### 1. Text Prompt & Images → `send_request()`

**Called by:**
```python
self.get_response()
```

**Delegates to:**
```python
send_request(prompt, assistant_name, previous_response_id, image_paths)
```

📍 Located in: `repositories/assistant_gpt_repository.py`

**What it does:**
- Loads assistant configuration (`ASSISTANTS` registry)
- Builds developer context depending on assistant type
- Builds API payload
- Sends request to OpenAI's `/v1/responses`
- Parses & formats the assistant's JSON response

---

### 2. File Upload → `process_single_*()` functions

**Called by:**
```python
self.upload_file()
```

**Delegates to:**
```python
process_single_pdf(...)          
process_single_docx(...)         
process_single_spreadsheet(...)  
```

📍 Located in: `files_intake/vector_db.py`

**What it does:**
- Uses `DocumentConverter` to extract content
- Chunks the content with `HybridChunker`
- Builds metadata and saves vectorized chunks into LanceDB
- Avoids duplicates with `is_duplicate()`

---

### 3. Website Processing → `process_entire_website()` or `process_single_webpage()`

**Called by:**
```python
self.process_website_from_gui()
```

**Delegates to:**
```python
process_entire_website(...)      
process_single_webpage(...)      
```

📍 Located in: `files_intake/vector_db.py`

**What it does:**
- Extracts content from web pages using sitemap or crawling
- Converts + chunks + stores them like file input

---

## ✅ Summary of What Tkinter Calls Outside Itself

| GUI Method                | Calls                          | Source Module                   |
|---------------------------|----------------------------------|----------------------------------|
| `get_response()`          | `send_request()`                | `assistant_gpt_repository.py`    |
|                           | `developer_context()`           | `assistant_gpt_repository.py`    |
|                           | `manage_response_*()`           | `assistant_gpt_repository.py`    |
| `upload_file()`           | `process_single_*()`            | `vector_db.py`                   |
|                           | → `DocumentConverter`, etc.     | `docling`, `files_intake`        |
| `process_website_from_gui()` | `process_entire_website()` / `process_single_webpage()` | `vector_db.py` |

---



