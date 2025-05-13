from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from inference import generate_answer  # make sure this imports your function correctly

app = FastAPI()

# Optional: Enable CORS if you're calling this from a frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class QueryInput(BaseModel):
    query: str

# Health check route
@app.get("/")
def read_root():
    return {"message": "SSAA Chatbot API is up and running!"}

# Query endpoint
@app.post("/query")
def query_route(request: QueryInput):
    # Get the generated answer
    answer = generate_answer(request.query)
    return {"answer": answer}
