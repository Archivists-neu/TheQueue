from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Create a Blueprint for NGO routes
users = Blueprint("users", __name__)


@users.route("/users", methods=["GET"])
def get_all_users():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /users')
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")
        email = request.args.get("email")
        dob = request.args.get("dob")
        query = "SELECT * FROM users WHERE 1=1"
        params = []

        if first_name:
            query += " AND first_name = %s"
            params.append(first_name)
        if last_name:
            query += " AND last_name = %s"
            params.append(last_name)
        if email:
            query += " AND email = %s"
            params.append(email)
        if dob:
            query += " AND dob = %s"
            params.append(dob)

            cursor.execute(query, params)
            user_list = cursor.fetchall()

            current_app.logger.info(f'Retrieved {len(user_list)} users')
            return jsonify(user_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_users: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


