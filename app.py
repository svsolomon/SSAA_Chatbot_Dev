from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from inference import generate_answer  # Ensure this correctly imports the answer generation logic

# Initialize the FastAPI app
app = FastAPI()

# Enable CORS to allow requests from other domains (e.g., frontend apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected structure of the request body for POST /query
class QueryInput(BaseModel):
    query: str

@app.get("/")
def read_root():
    """
    Health check route to confirm the API is running.
    
    Returns:
        dict: A simple message indicating the API status.
    """
    return {"message": "SSAA Chatbot API is up and running!"}

@app.post("/query")
def query_route(request: QueryInput):
    """
    Handles user queries by calling the answer generation function.

    Args:
        request (QueryInput): The user's query wrapped in a Pydantic model.

    Returns:
        dict: Contains the generated answer, list of matched documents, and flag status.
    """
    answer, documents, status = generate_answer(request.query)
    return {"answer": answer, "documents": documents, "status": status}
