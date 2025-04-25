import os
from sentence_transformers import SentenceTransformer
import faiss
import json
import openai
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from dotenv import load_dotenv
load_dotenv()


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

# def get_answer_from_openai(query: str, content: str, model: str = "gpt-3.5-turbo-0125") -> str:
#     """
#     Uses OpenAI's ChatCompletion API to answer a question based on the provided context.

#     Args:
#         query (str): The user's question.
#         content (str): The context/content from which the answer should be extracted.
#         model (str): OpenAI model to use (default is gpt-3.5-turbo-0125).

#     Returns:
#         str: The generated answer from OpenAI.
#     """
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
#                 {"role": "user", "content": f"Context: {content}\n\nQuestion: {query}"}
#             ],
#             stream=True,
#             temperature=0.2,
#             max_tokens=300
#         ) 
#         return response.choices[0].message.content.strip()

#     except Exception as e:
#         return f"Error occurred: {e}"

def get_answer_from_openai(query: str, content: str, model: str = "gpt-3.5-turbo-0125"):
    """
    Streams an answer from OpenAI based on provided context and query.
    Yields chunks of the response for real-time display.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the given context."},
                {"role": "user", "content": f"Context: {content}\n\nQuestion: {query}"}
            ],
            stream=True,
            temperature=0.2,
            max_tokens=300
        ) 
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"Error occurred: {e}"


def generate_answer(query):
    results = search_index(query, index, metadata_list, model)
    context = ''.join(res['text'] for res in results)
    return get_answer_from_openai(query, context)
