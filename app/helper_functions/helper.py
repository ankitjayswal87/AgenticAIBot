import requests
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import openpyxl
from PIL import Image
import zipfile
import re
import subprocess
import os
from PyPDF2 import PdfWriter

def is_valid_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        # Attempt to read the number of pages to verify integrity
        _ = len(reader.pages)
        return True
    except Exception:
        return False
    
def get_pdf_page_count(file_path):
    try:
        reader = PdfReader(file_path)
        return len(reader.pages)
    except Exception as e:
        return f"Error: {e}"
    
def is_valid_word(file_path):
    try:
        doc = Document(file_path)
        # Attempt to access paragraphs to verify layout structure
        _ = doc.paragraphs
        return True
    except Exception:
        return False
    
def get_word_page_count(file_path):
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
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verifies the file structure without loading full data
        return True
    except Exception:
        return False
    
def get_image_page_count(file_path):
    try:
        with Image.open(file_path) as img:
            # Check if the image format supports multiple frames/pages
            if hasattr(img, "n_frames"):
                return img.n_frames
            return 1 # Standard single-page images
    except Exception as e:
        return f"Error: {e}"
    
def is_valid_xlsx(file_path):
    try:
        # read_only=True speeds up validation by avoiding loading all data into memory
        wb = openpyxl.load_workbook(file_path, read_only=True)
        # Accessing sheet names forces the parser to read the file structure
        _ = wb.sheetnames
        wb.close()
        return True
    except Exception:
        return False
    
def get_xlsx_sheet_count(file_path):
    try:
        # read_only=True speeds up loading by skipping full data parsing
        wb = openpyxl.load_workbook(file_path, read_only=True)
        count = len(wb.sheetnames)
        wb.close()
        return count
    except Exception:
        return 0

def download_file_to_disk(media_url,file_name):
    file_name = "/var/www/html/PrintDocs/"+str(file_name)
    response = requests.get(media_url, allow_redirects=True)
    with open(file_name, "wb") as file:
        file.write(response.content)
        
def word_to_pdf(word_file, output_dir):
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        word_file
    ], check=True)

    pdf_file = os.path.join(
        output_dir,
        os.path.splitext(os.path.basename(word_file))[0] + ".pdf"
    )

    return pdf_file

def merge_mixed_files(output_path, file_list, target_width_pt=595):
    merger = PdfWriter()
    temp_pdfs = []
    
    file_count = 0

    for file in file_list:
        if file.lower().endswith('.pdf'):
            merger.append(file)
            file_count +=1
        elif file.lower().endswith(('.png', '.jpg', '.jpeg')):
            #print(f"Merging for {file}")
            img = Image.open(file)
            img_converted = img.convert('RGB')

            # Calculate high-res target size keeping aspect ratio
            orig_w, orig_h = img_converted.size
            aspect_ratio = orig_h / orig_w

            # Target width in points (standard A4 is 500-600pt)
            new_w = target_width_pt
            new_h = int(new_w * aspect_ratio)

            temp_pdf_name = f"temp_{os.path.basename(file)}.pdf"

            # Save using resolution parameter (72 dpi maps 1 px -> 1 pt in PDF)
            img_converted.save(
                temp_pdf_name,
                "PDF",
                resolution=72.0,
                save_all=True
            )

            merger.append(temp_pdf_name)
            file_count +=1
            temp_pdfs.append(temp_pdf_name)

    with open(output_path, "wb") as f:
        merger.write(f)

    merger.close()

    # Clean up temporary files
    for temp_file in temp_pdfs:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    print(f"Successfully merged into: {output_path}")
    output = {"response":"success","final_doc":output_path,"file_count":file_count}
    return output