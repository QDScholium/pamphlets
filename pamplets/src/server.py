import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from psycopg2.extras import Json

from src.main import process_document_ocr, get_markdown, store_markdown
import asyncio
from pymongo import MongoClient
import gridfs

load_dotenv()

app = FastAPI(title="Pamplets OCR API", description="API for OCR processing using Mistral")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)
mongo_url = os.environ.get("MONGO_URL")

mongo_client = MongoClient(mongo_url)
db = mongo_client["pamphlets"]  # Database for storing uploaded documents and metadata
fs = gridfs.GridFS(db)
backend_url = os.environ.get("BACKEND_URL")

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

    file_bytes = await file.read()
    file_id = fs.put(file_bytes, filename=file.filename, content_type="application/pdf")
    file_url = f"{backend_url}/files/{file_id}"
    print(f"Generated file URL: {file_url}")
    try: 
        ocr_result = await asyncio.to_thread(process_document_ocr, file_url)
        if not ocr_result:
            raise Exception("OCR processing returned empty result")
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        return JSONResponse(status_code=500, content={"message": f"OCR processing failed: {str(e)}"})

    article_id = str(file_id)
    try:
        stored = await asyncio.to_thread(store_markdown, ocr_result, article_id)
        if not stored:
            raise Exception("Storing markdown failed.")
    except Exception as e:
        raise Exception("Error storing markdown: " + str(e))
    return {"article_id": article_id}

@app.get("/files/{file_id}")
async def get_file(file_id: str):
    """
    Endpoint to serve files stored in MongoDB GridFS as PDFs.
    """
    try:
        from bson.objectid import ObjectId
        obj_id = ObjectId(file_id)
        grid_out = fs.get(obj_id)
        return Response(content=grid_out.read(), media_type="application/pdf")
    except Exception as e:
        print(f"Error retrieving file: {str(e)}")  # Log the actual error
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    
@app.get("/articles/{article_id}")
async def get_article(article_id: str):
    """
    Endpoint to retrieve an article by its ID.
    
    Args:
        article_id: The unique identifier for the article.
        
    Returns:
        The article content if found, or a 404 error if not found.
    """
    try:
        article_content = get_markdown(article_id)
        if article_content:
            return article_content
        else:
            raise HTTPException(status_code=404, detail="Article not found")
    except Exception as e:
        print(f"Error retrieving article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve article: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)