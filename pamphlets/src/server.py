import os
import io
import asyncio
import gridfs
from pymongo import MongoClient

from fastapi import FastAPI, HTTPException, UploadFile, File, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from dotenv import load_dotenv
from psycopg2.extras import Json # KEEP THIS HERE 

from src.main import get_markdown, store_markdown
from src.document_processing import read_document
from src.image_processing import read_image

load_dotenv()

app = FastAPI(title="Pamplets OCR API", description="API for OCR processing using Mistral")
# I hate CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pamphlets.scholium.ai/", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/ping")
async def ping():
    return {"status": "Pong"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    is_document = file.content_type == "application/pdf"
    try:
        if file.content_type == "application/pdf":
            article_id, ocr_result = await read_document(file)

        elif file.content_type in ["image/jpeg", "image/png"]:
            article_id, ocr_result = await read_image(file)
        else:
            return JSONResponse(
                status_code=400, 
                content={"message": "Only PDF, JPEG, and PNG files are supported"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    try:

        retry_count = 3
        stored = False
        for attempt in range(retry_count):
            try:
                stored = await asyncio.to_thread(store_markdown, ocr_result, article_id)
                if stored:
                    break
            except Exception as e:
                print(f"Attempt {attempt+1}/{retry_count} failed: {str(e)}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(1)  # Wait before retrying
        if not stored:
            return JSONResponse(status_code=500, content={"message": "Failed to store document content"})
    except Exception as e:
        raise e
    
    # After successfully storing the markdown, delete the original file from GridFS
    if is_document:
        try:
            from bson.objectid import ObjectId
            obj_id = ObjectId(article_id)
            fs.delete(obj_id)
            print(f"Successfully deleted file {article_id} from MongoDB GridFS")
        except Exception as e:
            print(f"Warning: Could not delete file from GridFS: {str(e)}")
            
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