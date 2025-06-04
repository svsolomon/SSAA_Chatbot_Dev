import os
from sentence_transformers import SentenceTransformer
import faiss
import json
import openai
import warnings
from utils import download_all_files_in_folder, download_blob_from_storage
from dotenv import load_dotenv

# Suppress user warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables from .env file
load_dotenv()

# Define cloud storage folder and local model directory
model_folder = "Models"                       
local_model_folder = "./models"  # Directory to save downloaded model files locally

# Create the local model directory if it doesn't exist
os.makedirs(local_model_folder, exist_ok=True)

# Download model files from storage
download_all_files_in_folder(model_folder, local_model_folder)

# Download vector index and metadata from cloud storage
download_blob_from_storage('indexer', './vector_index.faiss')
download_blob_from_storage('metadata.json', './metadata.json')

# Load sentence embedding model from local folder
model = SentenceTransformer('models/my_miniLM_model')

# Load FAISS index and metadata
index = faiss.read_index("vector_index.faiss")
with open("metadata.json", "r") as f:
    metadata_list = json.load(f)

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


def search_index(query, index, metadata_list, model, top_k=3):
    """
    Searches the FAISS vector index using a semantic embedding of the query.

    Args:
        query (str): The user query.
        index (faiss.Index): The FAISS index object.
        metadata_list (list): List of metadata corresponding to each vector.
        model (SentenceTransformer): The embedding model.
        top_k (int): Number of top matches to return.

    Returns:
        list: List of dictionaries containing matched document previews and scores.
    """
    query_vec = model.encode([query])
    D, I = index.search(query_vec, top_k)
    results = []
    for idx in I[0]:
        metadata = metadata_list[idx]
        results.append({
            "document": metadata["document"],
            "page_number": metadata["page_number"],
            "text": metadata["text"][:500],  # preview text
            "score": D[0][list(I[0]).index(idx)]
        })
    return results


def get_answer_from_openai(query: str, content: str, model: str = "gpt-3.5-turbo-0125"):
    """
    Uses OpenAI Chat Completion API to answer a query based on provided context.

    Args:
        query (str): User's question.
        content (str): Contextual information to base the answer on.
        model (str): OpenAI model name.

    Returns:
        str: The generated answer or an error message.
    """
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
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {e}"


def query_flagging(query: str, model: str = "gpt-3.5-turbo-0125") -> str:
    """
    Flags queries related to insurance or liability using a binary classification via LLM.

    Args:
        query (str): The user's query.
        model (str): OpenAI model name.

    Returns:
        str: "1" if query is about insurance/liability, otherwise "0".
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return 1 if the user's query is related to insurance or liability. Otherwise, return 0. Reply with only 1 or 0."},
                {"role": "user", "content": query}
            ],
            temperature=0.0,
            max_tokens=1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error occurred: {e}"


def generate_answer(query):
    """
    Generates an answer for a user query by:
    1. Flagging if it's insurance-related.
    2. Retrieving relevant indexed documents.
    3. Getting an answer from OpenAI based on retrieved context.

    Args:
        query (str): The user's question.

    Returns:
        tuple: (answer (str), list of matched documents, flag status)
    """
    status = query_flagging(query)
    results = search_index(query, index, metadata_list, model)
    documents = list(set(res['document'] for res in results))
    context = ''.join(res['text'] for res in results)
    answer = get_answer_from_openai(query, context)
    return answer, documents, status
