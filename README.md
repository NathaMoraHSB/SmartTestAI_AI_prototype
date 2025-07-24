
# 🧠 SmartTestAI GUI – Assistant Responses App

This project is a **graphical user interface (GUI)** built with **Tkinter** that allows users to interact with different AI assistants powered by OpenAI’s **Responses API**. It supports uploading files, images, and web pages, and provides tailored assistant responses based on the selected assistant type.

---

## 🚀 Features

### ✅ Assistant Types

You can choose between different assistant types for specialized tasks:
- **Exploratory Testing**: Helps design test cases based on context.
- **Interview Preparation**: Generates potential interview questions.
- **Summarizing**: Summarizes input content (e.g., reports).
- **Test Results**: Analyzes and formats tables of test results.

---

## 📚 Functionalities Explained

### 📁 1. File Upload & Processing

- Supported file types: **PDF, DOCX, CSV, XLSX**
- After uploading:
  - Files are **copied** to a local folder (`files/`)
  - Each file is **parsed** and stored in a **vector database** (LanceDB)
  - Metadata (file name, pages, etc.) is also stored

**How it works internally:**
```python
process_single_pdf(), process_single_docx(), process_single_spreadsheet()
```
Each function parses the content and prepares it for semantic search later via LanceDB.

---

### 🖼️ 2. Image Attachment

- Users can attach one or more **images (JPEG, PNG)** to their query
- These are **encoded in base64** and sent directly to the API as visual input

**Purpose:**
Useful when you want the assistant to analyze or consider visual data along with your text input.

---

### 🔗 3. Web Page or Website Parsing

- Enter a **URL** in the input field
- You can choose between:
  - Parsing a **single page**
  - Crawling and processing the **entire website**

**Internal processing:**
```python
process_single_webpage(), process_entire_website()
```
Extracts the main content and stores it in the vector DB for semantic search.

---

### 🧠 4. Vector Database (LanceDB)

A lightweight **vector database** stores all processed file and web content for fast and intelligent retrieval.

- When you ask something (e.g., in Exploratory Testing), your prompt is **semantically compared** to the stored content
- The top matches (chunks) are retrieved and **prepended** to your prompt to give better, contextual answers

**Function:**
```python
get_vector_context(prompt)
```

---

## 🛠️ Tech Stack

- **Python 3**
- **Tkinter** for GUI
- **OpenAI Responses API**
- **LanceDB** for vector search
- **Requests** for HTTP calls
- **Base64** for image encoding

---

## 💡 How to Use

1. **Run the app:**
   ```bash
   python gui.py
   ```

2. **Select an assistant** (e.g., Exploratory Testing)

3. **Choose an input type:**
   - Enter a prompt
   - Upload a file
   - Attach an image
   - Submit a website

4. **Click "Send"** and the assistant will respond in the textbox.

---

## 📂 Project Structure

```
infrastructure/
├── gpt/
│   ├── models/
│   │   └── assistant_name.py          # Enum for assistant names
│   ├── configs/
│   │   └── assistant_registry.py      # System messages and output format per assistant
│   ├── repositories/
│   │   └── assistant_gpt_repository.py # Main logic for building and sending requests
│   └── files_intake/
│       └── vector_db.py               # Vector DB logic and file processors
gui.py                                 # GUI entry point
```

---

## 🔒 API Key Setup

Set your API key and base URL in the file:

```python
# assistant_env_config.py
API_KEY = "your_openai_api_key"
API_URL = "https://api.openai.com/v1/responses"
```

---

## ✅ Example Use Case

1. Upload a `report.docx`
2. Select the **Summarizing** assistant
3. Type: "Summarize key findings from the report"
4. Click **Send**
5. Get a formatted summary in the output box

---

## 📌 Notes

- Each assistant expects different structure in the response. The app handles the formatting accordingly.
- All files are processed and saved locally before being used in the request.
- If the assistant supports vector context (Exploratory, Interview), it will enhance responses using semantic retrieval.
