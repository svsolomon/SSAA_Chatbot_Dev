import os
from sentence_transformers import SentenceTransformer
import faiss
import json
import openai
import warnings
from utils import download_all_files_in_folder, download_blob_from_storage
warnings.filterwarnings("ignore", category=UserWarning)
from dotenv import load_dotenv
load_dotenv()


model_folder = "Models"                       # Folder name where the model is stored

# Local path to save the files
local_model_folder = "./models"  # Local directory where the model files will be saved

# Create a local directory to store the model if it doesn't exist
os.makedirs(local_model_folder, exist_ok=True)

download_all_files_in_folder(model_folder,local_model_folder)

blob_name = 'indexer'
download_path = './vector_index.faiss'
download_blob_from_storage(blob_name,download_path)

blob_name = 'metadata.json'
download_path = './metadata.json'
download_blob_from_storage(blob_name,download_path)



# Load embedding model
# model = SentenceTransformer('all-MiniLM-L6-v2')
model = SentenceTransformer('models/my_miniLM_model')
# Loading Indexer and metadata
index = faiss.read_index("vector_index.faiss")
with open("metadata.json", "r") as f:
    metadata_list = json.load(f)

# Set your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)  # Replace with your actual key

def search_index(query, index, metadata_list, model, top_k=3):
    query_vec = model.encode([query])
    D, I = index.search(query_vec, top_k)
    results = []
    for idx in I[0]:
        metadata = metadata_list[idx]
        results.append({
            "document": metadata["document"],
            "page_number": metadata["page_number"],
            "text": metadata["text"][:500],  # preview
            "score": D[0][list(I[0]).index(idx)]
        })
    return results

def get_answer_from_openai(query: str, content: str, model: str = "gpt-3.5-turbo-0125"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                {"role": "user", "content": f"Context: {content}\n\nQuestion: {query}"}
            ],
            temperature=0.2,
            max_tokens=300
        )
        # Access the correct content from the response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {e}"

def generate_answer(query):
    results = search_index(query, index, metadata_list, model)
    context = ''.join(res['text'] for res in results)
    return get_answer_from_openai(query, context)
