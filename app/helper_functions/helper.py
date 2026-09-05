import requests
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from PIL import Image
import zipfile
import re

def is_valid_pdf(file_path):
    file_path = "/var/www/html/PrintDocs/"+str(file_path)
    try:
        reader = PdfReader(file_path)
        # Attempt to read the number of pages to verify integrity
        _ = len(reader.pages)
        return True
    except Exception:
        return False
    
def get_pdf_page_count(file_path):
    file_path = "/var/www/html/PrintDocs/"+str(file_path)
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception as e:
        return f"Error: {e}"
    
def is_valid_word(file_path):
    file_path = "/var/www/html/PrintDocs/"+str(file_path)
    try:
        doc = Document(file_path)
        # Attempt to access paragraphs to verify layout structure
        _ = doc.paragraphs
        return True
    except Exception:
        return False
    
def get_word_page_count(file_path):
    file_path = "/var/www/html/PrintDocs/"+str(file_path)
    try:
        with zipfile.ZipFile(file_path) as docx:
            # Read the application properties XML file from the docx container
            app_xml = docx.read('docProps/app.xml').decode('utf-8')
            
            # Search for the <Pages> tags
            match = re.search(r"<Pages>(\d+)</Pages>", app_xml)
            
            if match:
                page_count = int(match.group(1))
                return page_count
            else:
                return "Not-Available"
            
    except Exception as e:
        print(f"Error reading file: {e}")
        return "Not-Available"

def is_valid_image(file_path):
    file_path = "/var/www/html/PrintDocs/"+str(file_path)
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verifies the file structure without loading full data
        return True
    except Exception:
        return False
    
def get_image_page_count(file_path):
    file_path = "/var/www/html/PrintDocs/"+str(file_path)
    try:
        with Image.open(file_path) as img:
            # Check if the image format supports multiple frames/pages
            if hasattr(img, "n_frames"):
                return img.n_frames
            return 1 # Standard single-page images
    except Exception as e:
        return f"Error: {e}"

def download_file_to_disk(media_url,file_name):
    file_name = "/var/www/html/PrintDocs/"+str(file_name)
    response = requests.get(media_url, allow_redirects=True)
    with open(file_name, "wb") as file:
        file.write(response.content)