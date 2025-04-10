from PIL import Image
from io import BytesIO
import base64
from multiprocessing import Pool
from fastapi import UploadFile, File
import uuid
import base64

from src.client import client

def convert_png_to_jpeg_base64(png_path: str, quality: int = 85) -> str:
    with Image.open(png_path) as img:
        rgb_img = img.convert("RGB")
        buffer = BytesIO()
        rgb_img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        base64_img = base64.b64encode(buffer.read()).decode("utf-8")
        return base64_img

def convert_base64_to_jpeg_base64(base64_image: str, quality: int = 85) -> str:
    """
    Convert an image in base64 format to JPEG base64 format.
    
    Args:
        base64_image: The base64 encoded image string
        quality: JPEG quality (1-100), default is 85
        
    Returns:
        Base64 encoded JPEG image string
    """
    try:
        image_data = base64.b64decode(base64_image)
        
        with Image.open(BytesIO(image_data)) as img:
            rgb_img = img.convert("RGB")
            
            buffer = BytesIO()
            rgb_img.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            
            jpeg_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            return jpeg_base64
    except Exception as e:
        print(f"Error converting base64 to JPEG base64: {e}")
        return None

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e: 
        print(f"Error: {e}")
        return None
    
def process_img_ocr(base64_image:str) -> str:
    """
    Process a document using Mistral's OCR capabilities.
    
    Args:
        file_url: The URL of the document to process
        
    Returns:
        The OCR response from Mistral
    """

    try:

        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}" 
            }
        )
        return ocr_response.model_dump()
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        raise type(e)(error_msg) from e
    
def encode_and_process_image(image_base64:str):
    """
    Encode an image from a file path and process it using OCR.
    
    Args:
        image_path: The file path to the image to be processed
        
    Returns:
        The OCR response from Mistral after processing the encoded image
    """
    try: 
        encoded_image = convert_base64_to_jpeg_base64(image_base64)
        if not encoded_image:
            raise ValueError("Invalid or empty image data")
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None
    return process_img_ocr(encoded_image)


def process_img_batch(image_list: list[str]) -> list[str]:
    '''
    Takes in a list of image URLS and batch encodes them. 
    '''
    
    with Pool(processes=4) as pool:
        results = pool.map(encode_and_process_image, image_list)
    return (results)

async def read_image(file: UploadFile = File(...)):
    if not file:
        return JSONResponse(status_code=400, content={"message": "No file uploaded"})
    file_bytes = await file.read()
    
    file_id = str(uuid.uuid4())[:16]
    
    base64_image = base64.b64encode(file_bytes).decode('utf-8')

    
    try:
        ocr_result = encode_and_process_image(base64_image)
        if not ocr_result:
            raise Exception("OCR processing returned empty result")
    except Exception as e:
        raise e
    
    return file_id, ocr_result

