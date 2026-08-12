from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

# Create a Blueprint for media routes
media = Blueprint("media", __name__)

# Adjust this set to match the actual media types allowed in your schema
VALID_MEDIA_TYPES = {"book", "movie", "game", "music"}


def _fetch_media(where_clause, params):
    """Shared helper for simple single-condition media lookups."""
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM media WHERE {where_clause}", params)
        return cursor.fetchall()
    finally:
        cursor.close()


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
            query += " AND summary LIKE %s"
            params.append(f"%{summary}%")
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


# Get a single piece of media by its id
@media.route("/media/<int:media_id>", methods=["GET"])
def get_media_by_id(media_id):
    try:
        current_app.logger.info(f'GET /media/{media_id}')
        media_list = _fetch_media("media_id = %s", (media_id,))

        if not media_list:
            current_app.logger.info(f'Media with id {media_id} not found')
            return jsonify({"error": f"Media with id {media_id} not found"}), 404

        return jsonify(media_list[0]), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_id: {e}')
        return jsonify({"error": str(e)}), 500


# Searching for media by type (aka only books, only games etc.)
@media.route("/media/type/<string:media_type>", methods=["GET"])
def get_media_by_type(media_type):
    try:
        current_app.logger.info(f'GET /media/type/{media_type}')
        media_list = _fetch_media("media_type = %s", (media_type,))

        current_app.logger.info(f'Retrieved {len(media_list)} media of type {media_type}')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_type: {e}')
        return jsonify({"error": str(e)}), 500


# Searching by author name
@media.route("/media/author/<string:author_name>", methods=["GET"])
def get_media_by_author(author_name):
    try:
        current_app.logger.info(f'GET /media/author/{author_name}')
        media_list = _fetch_media("author LIKE %s", (f"%{author_name}%",))

        current_app.logger.info(f'Retrieved {len(media_list)} media by author {author_name}')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_author: {e}')
        return jsonify({"error": str(e)}), 500


# Searching by title/name of media piece
@media.route("/media/title/<string:title_name>", methods=["GET"])
def get_media_by_title(title_name):
    try:
        current_app.logger.info(f'GET /media/title/{title_name}')
        media_list = _fetch_media("title LIKE %s", (f"%{title_name}%",))

        current_app.logger.info(f'Retrieved {len(media_list)} media with title matching {title_name}')
        return jsonify(media_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_media_by_title: {e}')
        return jsonify({"error": str(e)}), 500


# deleting a piece of media in case of duplicates or non-relevent types
@media.route("/media/<int:media_id>", methods=["DELETE"])
def delete_media(media_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'DELETE /media/{media_id}')

        # Check if the media exists first
        cursor.execute("SELECT * FROM media WHERE media_id = %s", (media_id,))
        existing_media = cursor.fetchone()

        if not existing_media:
            current_app.logger.info(f'Media with id {media_id} not found')
            return jsonify({"error": f"Media with id {media_id} not found"}), 404

        cursor.execute("DELETE FROM media WHERE media_id = %s", (media_id,))
        get_db().commit()

        current_app.logger.info(f'Deleted media with id {media_id}')
        return jsonify({"message": f"Media with id {media_id} deleted successfully"}), 200
    except Error as e:
        get_db().rollback()
        current_app.logger.error(f'Database error in delete_media: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Editing an existing piece of media
@media.route("/media/<int:media_id>", methods=["PUT"])
def update_media(media_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info(f'PUT /media/{media_id}')

        # Check if the media exists first
        cursor.execute("SELECT * FROM media WHERE media_id = %s", (media_id,))
        existing_media = cursor.fetchone()

        if not existing_media:
            current_app.logger.info(f'Media with id {media_id} not found')
            return jsonify({"error": f"Media with id {media_id} not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        if "media_type" in data and data["media_type"] not in VALID_MEDIA_TYPES:
            return jsonify({
                "error": f"Invalid media_type. Must be one of: {', '.join(sorted(VALID_MEDIA_TYPES))}"
            }), 400

        # Build the update dynamically based on which fields were provided
        allowed_fields = ["media_type", "title", "summary", "author"]
        fields_to_update = []
        params = []

        for field in allowed_fields:
            if field in data:
                fields_to_update.append(f"{field} = %s")
                params.append(data[field])

        if not fields_to_update:
            return jsonify({"error": "No valid fields provided to update"}), 400

        params.append(media_id)
        query = f"UPDATE media SET {', '.join(fields_to_update)} WHERE media_id = %s"

        cursor.execute(query, params)
        get_db().commit()

        # Return the updated record
        cursor.execute("SELECT * FROM media WHERE media_id = %s", (media_id,))
        updated_media = cursor.fetchone()

        current_app.logger.info(f'Updated media with id {media_id}')
        return jsonify(updated_media), 200
    except Error as e:
        get_db().rollback()
        current_app.logger.error(f'Database error in update_media: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Adding a new piece of media 
@media.route("/media", methods=["POST"])
def add_media():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('POST /media')

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Required fields to create a new piece of media
        required_fields = ["media_type", "title"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        if data["media_type"] not in VALID_MEDIA_TYPES:
            return jsonify({
                "error": f"Invalid media_type. Must be one of: {', '.join(sorted(VALID_MEDIA_TYPES))}"
            }), 400

        # Whitelist of fields allowed to be set
        allowed_fields = ["media_type", "title", "summary", "author"]
        fields_to_insert = [field for field in allowed_fields if field in data]
        values = [data[field] for field in fields_to_insert]

        columns = ", ".join(fields_to_insert)
        placeholders = ", ".join(["%s"] * len(fields_to_insert))
        query = f"INSERT INTO media ({columns}) VALUES ({placeholders})"

        cursor.execute(query, values)
        get_db().commit()

        new_media_id = cursor.lastrowid

        # Return the newly created record
        cursor.execute("SELECT * FROM media WHERE media_id = %s", (new_media_id,))
        new_media = cursor.fetchone()

        current_app.logger.info(f'Created new media with id {new_media_id}')
        return jsonify(new_media), 201
    except Error as e:
        get_db().rollback()
        current_app.logger.error(f'Database error in add_media: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()