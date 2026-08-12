from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error, IntegrityError

# Create a Blueprint for friendship routes
friendships = Blueprint("friendship", __name__)

# Must be present on create: the NOT NULL columns in ddl.sql that have no DEFAULT.
# friendship_id is AUTO_INCREMENT. NOTE: status is listed here but ddl.sql defaults
# it to 'pending', so it should move to the optional set when POST is written.
required_fields = ["requester_id", "addressee_id", "status", "date_requested"]

# Columns a client may change. Whitelisting these is what makes an f-string
# UPDATE safe from SQL injection, so never build it from raw request keys.
# Populate when PUT is written; date_requested belongs out of it as a creation fact.
updatable_fields = []


@friendships.route("/friendships", methods=["GET"])
def get_all_friendships():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /friendship/friendships')
        requester_id = request.args.get("requester_id")
        addressee_id = request.args.get("addressee_id")
        status = request.args.get("status")
        date_requested = request.args.get("date_requested")

        # friendship has no soft-delete column, so there is nothing to exclude here.
        # WHERE 1=1 lets the optional filters below append AND clauses cleanly.
        query = """
            SELECT friendship_id, requester_id, addressee_id, status,
                   date_requested, date_accepted
            FROM friendship
            WHERE 1=1
        """
        params = []

        if requester_id:
            query += " AND requester_id = %s"
            params.append(requester_id)
        if addressee_id:
            query += " AND addressee_id = %s"
            params.append(addressee_id)
        if status:
            query += " AND status = %s"
            params.append(status)
        if date_requested:
            query += " AND date_requested = %s"
            params.append(date_requested)

        cursor.execute(query, params)
        friendship_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(friendship_list)} friendships')
        return jsonify(friendship_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_friendships: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
