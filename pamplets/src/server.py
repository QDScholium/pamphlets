import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Pamplets OCR API", description="API for OCR processing using Mistral")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify the exact origin of your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly list allowed methods
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],  # Explicitly list allowed headers
)


try:
    api_key = os.environ["MISTRAL_API_KEY"]
except KeyError:
    print("Error: MISTRAL_API_KEY environment variable not found")
class OCRRequest(BaseModel):
    document_url: str

@app.get("/")
async def root():
    return {"message": "Health Check"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file:
        return JSONResponse(status_code=400, content={"message": "No file uploaded"})
    
    return {"message": f"Document '{file.filename}' received successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
