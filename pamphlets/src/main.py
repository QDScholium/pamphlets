import os
from mistralai import Mistral
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import Json

from src.image_processing import *
from src.client import client

load_dotenv()
connection_string = os.getenv('DATABASE_URL')

connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections in the pool
    10,  # Maximum number of connections in the pool
    connection_string
)
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
        return ocr_response.model_dump()
    except Exception as e:
        error_msg = f"OCR processing failed: {str(e)}"
        raise type(e)(error_msg) from e


def store_markdown(markdown:dict, id: str):
    """
    Store markdown content in the database with the given ID.
    
    Args:
        markdown: The markdown content to store
        id: The unique identifier for the markdown content
        
    Returns:
        True if storage was successful, False otherwise
    """
    conn = None 
    try:
        conn = connection_pool.getconn()
        table = "articles"
        with conn.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {table} (id, content, comments)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET content = EXCLUDED.content
            """, (id, Json(markdown), Json({})))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error storing markdown2: {str(e)}")
        return False
    finally:
        # Return the connection to the pool
        if conn:
            connection_pool.putconn(conn)

def get_markdown(id: str):
    """
    Retrieve markdown content from the database for the given ID.
    
    Args:
        id: The unique identifier for the markdown content.
        
    Returns:
        The markdown content as a dictionary if found, or None otherwise.
    """
    conn = None
    try:
        conn = connection_pool.getconn()
        table = "articles"
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT content FROM {table} WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                content = row[0]
                return content
            else:
                return None
    except Exception as e:
        print(f"Error retrieving markdown: {str(e)}")
        return None
    finally:
        if conn:
            connection_pool.putconn(conn)



if __name__ == "__main__":
    # file_url = "https://13a5-138-51-71-14.ngrok-free.app/files/67f309db84159383bd889930"
    # file_md = process_document_ocr(file_url)
    # print(type(file_md))
    # store_markdown(file_md,"67f309db84159383bd889930")
    # print(get_markdown("67f309db84159383bd889930"))

    # encoded_img = encode_image("sample_img.jpeg")
    # jpeg_img = convert_png_to_jpeg_base64("sample_img.jpeg")
    # print(f"Encoded image size: {len(encoded_img)} bytes")
    # print(f"JPEG image size: {len(jpeg_img)} bytes")
    # print(process_img_ocr(jpeg_img))
    
    images = ["./sample_imgs/sample_img.png", "./sample_imgs/sample_img2.png", 
              "./sample_imgs/sample_img3.png", "./sample_imgs/sample_img4.png", 
              "./sample_imgs/sample_img5.png"]
    # print(encode_and_process_image(images[0]))
    print(len(process_img_batch(images)))


