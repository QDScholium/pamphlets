import os
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File
import asyncio
from pymongo import MongoClient
import gridfs

from src.client import client

mongo_url = os.environ.get("MONGO_URL")

mongo_client = MongoClient(mongo_url)
db = mongo_client["pamphlets"]  # Database for storing uploaded documents and metadata
fs = gridfs.GridFS(db)
backend_url = os.environ.get("BACKEND_URL")

def process_document_ocr(file_url):
    """
    Process a document using Mistral's OCR capabilities.
    
    Args:
        file_url: The URL of the document to process
        
    Returns:
        The OCR response from Mistral
    """
    # The issue might be related to the URL format or validation
    if not file_url or not isinstance(file_url, str):
        raise ValueError(f"Invalid file_url provided: {file_url}")
    
    # Ensure the URL is properly formatted
    if not file_url.startswith(("http://", "https://")):
        raise ValueError(f"URL must start with http:// or https://: {file_url}")

    try:
        # Use the existing client but with explicit parameters
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": file_url.strip()  # Remove any whitespace
            },
            include_image_base64=True
        )
        return ocr_response.model_dump()
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        raise type(e)(error_msg) from e


async def read_document(file: UploadFile = File(...)):
    if not file:
        return JSONResponse(status_code=400, content={"message": "No file uploaded"})
    file_bytes = await file.read()
    file_id = fs.put(file_bytes, filename=file.filename, content_type="application/pdf")
    file_url = f"{backend_url}files/{file_id}"
    
    try: 
        ocr_result = await asyncio.to_thread(process_document_ocr, file_url)
        if not ocr_result:
            raise Exception("OCR processing returned empty result")
    except Exception as e:
        raise e

    article_id = str(file_id)
    return article_id, ocr_result