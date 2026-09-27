import logging
logger = logging.getLogger(__name__)

def insert_booking(
    account_id,
    phone,
    connection,
    booking_id,
    payment_link_id,
    amount,
    status,
    booking_details,
    payment_id=None
):
    """
    Insert a booking into the bookings table.
    """

    query = """
        INSERT INTO bookings
        (
            account_id,
            phone,
            booking_id,
            payment_link_id,
            payment_id,
            amount,
            status,
            booking_details
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    values = (
        account_id,
        phone,
        booking_id,
        payment_link_id,
        payment_id,
        amount,
        status,
        booking_details
    )

    cursor = connection.cursor()

    try:
        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        
def insert_salon_booking(
    account_id,
    phone,
    connection,
    booking_id,
    status,
    booking_details
):
    """
    Insert a booking into the salon_bookings table.
    """

    query = """
        INSERT INTO salon_bookings
        (
            account_id,
            phone,
            booking_id,
            status,
            booking_details
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    values = (
        account_id,
        phone,
        booking_id,
        status,
        booking_details
    )

    cursor = connection.cursor()

    try:
        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        
def get_appointment_count(connection, appointment_date, appointment_time):
    query = """
        SELECT COUNT(*) AS count
        FROM salon_bookings
        WHERE booking_details->>'$.appointment_date' = %s
          AND booking_details->>'$.appointment_time' = %s
          AND status = 'CONFIRMED'
    """

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, (appointment_date, appointment_time))
        result = cursor.fetchone()
        return result["count"]
    finally:
        cursor.close()
        
def mark_booking_status(connection, payment_link_id, payment_id, payment_status):
    query = """
        UPDATE bookings
        SET
            payment_id = %s,
            status = %s
        WHERE payment_link_id = %s
    """

    cursor = connection.cursor()

    try:
        cursor.execute(query, (payment_id, payment_status, payment_link_id))
        connection.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        
        
def get_booking_by_payment_link_id(connection, payment_link_id):
    query = """
        SELECT *
        FROM bookings
        WHERE payment_link_id = %s
    """

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, (payment_link_id,))
        return cursor.fetchone()

    finally:
        cursor.close()
        
def get_client_id_by_number(number_id,connection):
    
    cursor = connection.cursor()

    query = """
        SELECT client_id
        FROM did_numbers
        WHERE number_id = %s
          AND is_deleted = 0
        LIMIT 1
    """

    cursor.execute(query, (number_id,))
    result = cursor.fetchone()

    cursor.close()

    return result[0] if result else None
        

def insert_document(
    account_id,
    client_id,
    phone,
    workspace_id,
    conversation_id,
    message_id,
    content,
    message_type,
    media_url,
    page_count,
    document_type,
    connection
):
    """
    Insert a document/message into the documents table.
    """

    query = """
        INSERT INTO documents
        (
            account_id,
            client_id,
            phone,
            workspace_id,
            conversation_id,
            message_id,
            content,
            message_type,
            media_url,
            page_count,
            document_type
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    values = (
        account_id,
        client_id,
        phone,
        workspace_id,
        conversation_id,
        message_id,
        content,
        message_type,
        media_url,
        page_count,
        document_type
    )

    cursor = connection.cursor()

    try:
        cursor.execute(query, values)
        connection.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        

def get_document_file_paths(connection, document_ids, base_path):
    """
    Get document file paths from documents table.

    Args:
        connection: Existing MySQL database connection
        document_ids: Comma-separated document IDs.
                      Example: "2391,2393,2395"

    Returns:
        List of file paths in the same order as document_ids.
    """

    if not document_ids:
        return []

    try:
        # Convert comma-separated IDs to integers
        ids = [
            int(doc_id.strip())
            for doc_id in document_ids.split(",")
            if doc_id.strip()
        ]

        if not ids:
            return []

        cursor = connection.cursor()

        placeholders = ",".join(["%s"] * len(ids))

        query = f"""
            SELECT id, content,phone
            FROM documents
            WHERE id IN ({placeholders})
        """

        cursor.execute(query, ids)

        rows = cursor.fetchall()

        cursor.close()
        phone = rows[0][2]

        # Create lookup dictionary
        content_by_id = {
            row[0]: row[1]
            for row in rows
        }

        #base_path = "/var/www/html/PrintDocs/"

        # Preserve input ID order
        file_paths = [
            base_path + content_by_id[doc_id]
            for doc_id in ids
            if doc_id in content_by_id and content_by_id[doc_id]
        ],phone

        return file_paths

    except Exception as e:
        print(f"Error getting document file paths: {e}")
        return []