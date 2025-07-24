
# SmartTestAI - GPT-Powered Exploratory Testing Assistant

This is a Python-based prototype demonstrating how AI functionalities could be integrated into the real SmartTestAI application to support exploratory software testing. It showcases the potential use of advanced GPT features from OpenAI, including assistants for test design, interview preparation, and summarizing test logs. The prototype also includes experimental support for multimodal inputs and vector-based document retrieval.

## 🔧 Features

### 1. Exploratory Testing Design Assistant
This assistant receives project and test session metadata and guides the user through the creation of test objectives and procedures using a friendly, conversational tone. It combines system instructions, dynamic developer context, and user queries to generate structured outputs.

### 2. Interview Question Generator
Helps the user prepare structured interview questions for project stakeholders. This is useful for refining the exploratory testing focus and understanding the product context better.

### 3. Test Log Summarizer
Processes test logs and generates summaries that can be used to draft or improve final test reports. The assistant generates structured fields such as summaries and key insights.

### 4. Vector-Based Context Enrichment (Prototype)
An experimental feature that uses LanceDB to semantically store and retrieve information from uploaded documents (PDF, DOCX, XLSX) and web pages. These document chunks are retrieved and prepended to the prompt to provide richer answers. Although not integrated in the final production environment, this prototype demonstrates the feasibility of document-grounded assistants.

## 🧠 AI Integration

We experimented with different OpenAI APIs and settled on the **Responses API**, which supports:
- Structured output via `json_schema`
- Persistent context across requests
- Multimodal inputs (e.g., images)
- Reduced need for complex prompt engineering

This decision was based on its robustness and forward-compatibility compared to the Completions and Assistants APIs.

## 🧱 Message Structure and Roles

The OpenAI Responses API is designed to support multi-turn conversations using a fixed set of roles: `system`, `developer`, and `user`. In this prototype, we follow this structure to simulate how SmartTestAI would communicate with the API in a real-world application. The assistant receives each request in the following format:

- `system` role: Defines the assistant’s main task and expected behavior using static instructions stored in configuration files (e.g., `assistant_registry.py`). This prompt sets the foundational objective for how the assistant should respond and is designed to remain static within the backend, meaning it cannot be changed dynamically by the user.

- `developer` role: Intended to provide dynamic context retrieved from the backend—such as the project name, test session, and test object—formatted as a string and passed to the assistant. While this prototype does not include a connection to an SQL database, the final SmartTestAI application is designed to populate this role automatically based on project data stored in the backend.

- `user` role: Contains the actual user input. This message is enriched by SmartTestAI with additional context, including semantically relevant text retrieved from indexed documents (vector-based context) and optional images.

By structuring requests this way, the assistant receives both static and dynamic knowledge to produce accurate, context-aware responses.

## 🗃️ Vector Database (LanceDB)

The system includes a prototype that uses LanceDB to manage a vector database for semantic search. The flow is:
1. Extract content from PDF, DOCX, XLSX, or websites.
2. Embed text using OpenAI’s `text-embedding-3-large` model.
3. Store vectors and metadata (filename, pages, titles) in LanceDB.
4. On each user query, perform semantic search to retrieve relevant chunks.
5. Prepend the chunks to the user prompt to enrich assistant responses.

> ⚠️ LanceDB was not deployed on the final server, but remains a reusable in this experimental module.

## 📂 Supported Inputs

- **Text Input**: Normal user prompts.
- **Image Input**: JPG and PNG images are encoded in base64 and attached to the assistant input.
- **File Input** (Experimental): PDFs, spreadsheets, and DOCX files are converted to chunks for vector enrichment.
- **Link Input** (Experimental): Websites are scraped and indexed in LanceDB.

## 📦 Installation

```bash
git clone https://github.com/your-repo/smarttestai.git
cd smarttestai
pip install -r requirements.txt
```

> **Note:** To run the prototype successfully, you must create a `.env` file inside the `infrastructure` folder and include your OpenAI API key in the following format:
>
> ```env
> OPENAI_API_KEY=your_openai_key_here
> ```
>
> This key is required to authenticate requests sent to the OpenAI Responses API.


## 🚀 Running the App

```bash
python main_for_testing.py
```

This script is located in the folder `infrastructure/gpt/test_data/` and serves as the entry point to run the prototype locally.

## 📚 References

The following sources were consulted during the development of this prototype and guided the design and implementation of SmartTestAI's core features:


[1] OpenAI, “Completions,” OpenAI Platform Documentation, 2024. [Online]. https://platform.openai.com/docs/guides/completions  
[2] OpenAI, “Assistants API,” OpenAI Platform Documentation, 2024. [Online]. https://platform.openai.com/docs/assistants/overview  
[3] OpenAI, “Responses API,” OpenAI Platform Documentation, 2024. [Online]. https://platform.openai.com/docs/responses/overview  
[4] J. Briggs, “Build Document-Grounded GPT Assistants with Responses API,” YouTube, Mar. 22, 2024. https://www.youtube.com/watch?v=9lBTS5dM27c  
[5] J. Briggs, GitHub repository, https://github.com/jamesbriggs/openai-responses-api-demo

---
Nathalia C. Mora A.
