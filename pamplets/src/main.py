import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

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
        return ocr_response
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        raise type(e)(error_msg) from e
    
if __name__ == "__main__":
    file_url = "https://13a5-138-51-71-14.ngrok-free.app/files/67f309db84159383bd889930"
    print(process_document_ocr(file_url))