from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Create a Blueprint for media routes
media = Blueprint("media", __name__)

@media.route("/media", methods=["GET"])
def get_all_media():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /media')
        media_id = request.args.get("media_id")
        media_type = request.args.get("media_type")
        title = request.args.get("title")
        summary = request.args.get("summary")
        query = "SELECT * FROM users WHERE 1=1"
        params = []

        if media_id:
            query += " AND media_id = %s"
            params.append(media_id)
        if media_type:
            query += " AND media_type = %s"
            params.append(media_type)
        if title:
            query += " AND title = %s"
            params.append(title)
        if summary:
            query += " AND summary = %s"
            params.append(summary)

        cursor.execute(query, params)
        media_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(media_list)} media')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_media: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
