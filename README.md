# 🧠 SSAA AI Chatbot

This repository hosts an AI-powered chatbot system developed for the **Self Storage Association of Australasia (SSAA)**. It enables users to interact with SSAA documentation via natural language queries, providing instant and accurate answers using retrieval-augmented generation (RAG) and OpenAI's language models.

---

## 📁 Repository Structure

| File / Folder        | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `.env`               | Contains API keys (OpenAI) and Azure Blob Storage connection strings        |
| `.gitignore`         | Specifies files and folders to ignore when pushing to GitHub                |
| `app.py`             | FastAPI backend exposing an API endpoint for query processing               |
| `chatbot.py`         | Streamlit frontend that communicates with the FastAPI backend               |
| `inference.py`       | Implements query flagging, FAISS search, and OpenAI-based answer generation |
| `utils.py`           | Utilities for downloading files (e.g., FAISS index, metadata, model) from Azure |
| `data_ingestion.ipynb` | Jupyter Notebook for uploading/downloading documents from Azure           |
| `development.ipynb`  | Jupyter Notebook for preprocessing, indexing, and inference development     |

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **OpenAI GPT Models**
- **FAISS (Facebook AI Similarity Search)** for vector indexing
- **Sentence-Transformers** for generating embeddings
- **FastAPI** for backend API
- **Streamlit** for frontend interface
- **Azure Blob Storage** for document and model storage

---

## 🔁 Workflow

1. **Upload Documents**
   - Use `data_ingestion.ipynb` to:
     - Upload new PDF/DOCX files to Azure Blob Storage
     - Delete or list existing files

2. **Preprocess & Index**
   - Open `development.ipynb` and run:
     1. Preprocessing to:
        - Extract text from documents
        - Remove duplicates
        - Create metadata for each page
     2. Generate sentence embeddings using a pre-trained model
     3. Index document vectors using FAISS
     4. Save the FAISS index and metadata

3. **Run Backend**
   - Start the FastAPI server:
     ```bash
     uvicorn app:app --reload
     ```

4. **Start Chatbot Interface**
   - Run the Streamlit app:
     ```bash
     streamlit run chatbot.py
     ```

5. **Query Inference Pipeline**
   - When a query is entered:
     1. The query is flagged if it's irrelevant or harmful
     2. A vector representation of the query is generated
     3. FAISS retrieves top matching content
     4. Retrieved content and query are sent to OpenAI's model
     5. The final answer is returned to the user
---

Note: The user only needs to interact with the front-end (Chatbot UI) by asking queries. This will cause the backend api to be called which will run the inference pipeline and returns the answer as the reponse which will be displayed to the user along with the metadata and disclaimer message. 


## ⚡ Powered By

- [OpenAI](https://openai.com/)
- [Azure Blob Storage](https://azure.microsoft.com/en-au/services/storage/blobs/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
