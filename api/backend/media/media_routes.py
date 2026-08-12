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
        author = request.args.get("author")

        query = "SELECT * FROM media WHERE 1=1"
        params = []

        if media_id:
            query += " AND media_id = %s"
            params.append(media_id)
        if media_type:
            query += " AND media_type = %s"
            params.append(media_type)
        if title:
            query += " AND title LIKE %s"
            params.append(f"%{title}%")
        if summary:
            query += " AND summary = %s"
            params.append(summary)
        if author:
            query += " AND author LIKE %s"
            params.append(f"%{author}%")

        cursor.execute(query, params)
        media_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(media_list)} media')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_media: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

 # Searching for media by type (aka only books, only games etc.)
@media.route("/media/type/<string:media_type>", methods=["GET"])
def get_media_by_type(media_type):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /media/type/{media_type}')
        query = "SELECT * FROM media WHERE media_type = %s"
        cursor.execute(query, (media_type,))
        media_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(media_list)} media of type {media_type}')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_type: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Searching by author name 
@media.route("/media/author/<string:author_name>", methods=["GET"])
def get_media_by_author(author_name):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /media/author/{author_name}')
        query = "SELECT * FROM media WHERE author LIKE %s"
        cursor.execute(query, (f"%{author_name}%",))
        media_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(media_list)} media by author {author_name}')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_author: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Searching by name of media piece 
@media.route("/media/title/<string:title_name>", methods=["GET"])
def get_media_by_title(title_name):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'GET /media/title/{title_name}')
        query = "SELECT * FROM media WHERE title LIKE %s"
        cursor.execute(query, (f"%{title_name}%",))
        media_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(media_list)} media with title matching {title_name}')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_title: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()