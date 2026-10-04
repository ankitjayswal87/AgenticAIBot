import faulthandler
faulthandler.enable()

import os
import uuid
import json
import logging
import gc
from pathlib import Path
import posixpath
from urllib.parse import urlparse
from dotenv import load_dotenv

from flask import Flask, jsonify, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mysql.connector
from mysql.connector import pooling

# Internal imports
from constants import constant
from db_operations import pass_booking
from helper_functions import helper

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

app = Flask(__name__)

# 1. Use Redis for rate limiting in production to avoid in-memory state bloat.
# Replace with your Redis URI, or use a external cache backend.
# REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6379")
# limiter = Limiter(
#     key_func=get_remote_address,
#     app=app,
#     storage_uri=REDIS_URI,
#     default_limits=["1000000 per day", "100000 per hour"]
# )

# 2. Database Connection Pooling
db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    pool_reset_session=True,
    host=constant.MYSQL_DB_HOST,
    user=constant.MYSQL_DB_USER,
    password=constant.MYSQL_DB_PASS,
    database=constant.MYSQL_DB
)

def get_db():
    """Retrieves a database connection from the pool for the current request."""
    if 'db' not in g:
        g.db = db_pool.get_connection()
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    """Ensures database connections are returned to the pool after every request."""
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()


@app.route('/agentic_ai/merge_files', methods=['POST'])
def merge_files_api():
    logger.info("MERGING FILES PRINT APP===")
    some_json = request.get_json() or {}
    logger.info("MERGE REQUEST: %s", some_json)

    doc_ids = some_json.get("doc_ids", "")
    logger.info("DOC IDS: %s", doc_ids)

    try:
        conn = get_db()
        file_paths, phone = pass_booking.get_document_file_paths(conn, doc_ids, constant.PRINT_DOCS_PATH)
        logger.info("MERGE FILE PATHS: %s", file_paths)
        logger.info("MERGE FILE FOR CUSTOMER: %s", phone)
        
        merged_doc_name = f"{constant.PRINT_DOCS_PATH}final_{phone}_document.pdf"
        output = helper.merge_mixed_files(merged_doc_name, file_paths)

        return jsonify(output)
    except Exception as e:
        logger.error("merge_files api failed: %s", e, exc_info=True)
        return jsonify({"response": "fail"}), 500
    finally:
        # Force garbage collection to free large PDF conversion buffers
        gc.collect()


@app.route('/agentic_ai/print_app', methods=['POST'])
def print_app_api():
    logger.info("PRINT APP===")
    some_json = request.get_json() or {}
    logger.info("WhatsAppMessage: %s", some_json)

    event = some_json.get("event", "")
    workspace_id = some_json.get("workspaceId", "")

    data = some_json.get("data", {})
    conversation_id = data.get("conversationId", "")
    message_id = data.get("messageId", "")
    message_type = data.get("messageType", "")
    mime_type = data.get("mimeType", "")
    media_url = data.get("mediaUrl", "")
    account_id = data.get("accountId", "")

    contact = data.get("contact", {})
    phone = contact.get("phone", "")

    if event == "test.ping":
        return jsonify({"response": ""})

    if message_type in ("document", "image"):
        try:
            conn = get_db()
            client_id = pass_booking.get_client_id_by_number(account_id, conn)
            logger.info("Client ID: %s", client_id)

            document_type = "unknown"
            page_count = "Not-Available"

            parsed_url = urlparse(media_url)
            content = posixpath.basename(parsed_url.path)
            extension = os.path.splitext(content)[1].lower()

            helper.download_file_to_disk(media_url, content)
            local_url = f"{constant.HTTP_SCHEMA}://{constant.SERVER_HOST}/PrintDocs/{content}"
            doc_file_path = f"{constant.PRINT_DOCS_PATH}{content}"

            if extension == ".pdf":
                document_type = "pdf"
                if helper.is_valid_pdf(doc_file_path):
                    page_count = helper.get_pdf_page_count(doc_file_path)
                    logger.info("PDF-FileName: %s PDF-Pages: %s", content, page_count)

            elif extension in (".docx", ".doc", ".odt", ".dotx"):
                document_type = "word"
                if helper.is_valid_word(doc_file_path):
                    page_count = helper.get_word_page_count(doc_file_path)
                    helper.word_to_pdf(doc_file_path, constant.PRINT_DOCS_PATH)
                    content = os.path.splitext(os.path.basename(doc_file_path))[0] + ".pdf"
                    page_count = helper.get_pdf_page_count(f"{constant.PRINT_DOCS_PATH}{content}")
                    local_url = f"{constant.HTTP_SCHEMA}://{constant.SERVER_HOST}/PrintDocs/{content}"

            elif extension in (".pptx", ".ppt"):
                document_type = "powerpoint"
                if helper.is_valid_ppt(doc_file_path):
                    page_count = helper.get_pptx_slide_count(doc_file_path)
                    helper.powerpoint_to_pdf(doc_file_path, constant.PRINT_DOCS_PATH)
                    content = os.path.splitext(os.path.basename(doc_file_path))[0] + ".pdf"
                    page_count = helper.get_pdf_page_count(f"{constant.PRINT_DOCS_PATH}{content}")
                    local_url = f"{constant.HTTP_SCHEMA}://{constant.SERVER_HOST}/PrintDocs/{content}"

            elif extension in (".xlsx", ".xls"):
                document_type = "xlsx"
                if helper.is_valid_xlsx(doc_file_path):
                    page_count = helper.get_xlsx_sheet_count(doc_file_path)

            elif extension in (".", "", ".bin"):
                logger.info("Handling files with empty extension")
                if helper.is_valid_pdf(doc_file_path):
                    document_type = "pdf"
                    page_count = helper.get_pdf_page_count(doc_file_path)
                elif helper.is_valid_word(doc_file_path):
                    document_type = "word"
                    helper.word_to_pdf(doc_file_path, constant.PRINT_DOCS_PATH)
                    content = os.path.splitext(os.path.basename(doc_file_path))[0] + ".pdf"
                    page_count = helper.get_pdf_page_count(f"{constant.PRINT_DOCS_PATH}{content}")
                    local_url = f"{constant.HTTP_SCHEMA}://{constant.SERVER_HOST}/PrintDocs/{content}"
                elif helper.is_valid_ppt(doc_file_path):
                    document_type = "powerpoint"
                    helper.powerpoint_to_pdf(doc_file_path, constant.PRINT_DOCS_PATH)
                    content = os.path.splitext(os.path.basename(doc_file_path))[0] + ".pdf"
                    page_count = helper.get_pdf_page_count(f"{constant.PRINT_DOCS_PATH}{content}")
                    local_url = f"{constant.HTTP_SCHEMA}://{constant.SERVER_HOST}/PrintDocs/{content}"
                elif helper.is_valid_xlsx(doc_file_path):
                    document_type = "xlsx"
                    page_count = helper.get_xlsx_sheet_count(doc_file_path)
                elif helper.is_valid_image(doc_file_path):
                    document_type = "image"
                    page_count = helper.get_image_page_count(doc_file_path)

            elif mime_type.split("/")[0].lower() == "image":
                document_type = "image"
                if helper.is_valid_image(doc_file_path):
                    page_count = helper.get_image_page_count(doc_file_path)

            document_id = pass_booking.insert_document(
                account_id=account_id,
                client_id=client_id,
                phone=phone,
                workspace_id=workspace_id,
                conversation_id=conversation_id,
                message_id=message_id,
                content=content,
                message_type=message_type,
                media_url=local_url,
                page_count=page_count,
                document_type=document_type,
                connection=conn
            )
            logger.info("Document ID: %s", document_id)

            return jsonify({"response": ""})
        except Exception as e:
            logger.error("print_app_api failed: %s", e, exc_info=True)
            return jsonify({"response": "print app api failed"}), 500
        finally:
            gc.collect()
    else:
        return jsonify({"response": ""})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006)