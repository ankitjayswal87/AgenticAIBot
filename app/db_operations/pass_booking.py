#import mysql.connector

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