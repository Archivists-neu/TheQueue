from flask import Blueprint, request, jsonify
from backend.db_connection import get_db

# Genre Blueprint
genres = Blueprint("genres", __name__)


# GET ALL GENRES
@genres.route("/genre", methods=["GET"])
def get_genres():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT genre_id, name, description
            FROM genre
            ORDER BY name;
        """)

        genre_list = cursor.fetchall()

        return jsonify(genre_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


# ADD NEW GENRE
@genres.route("/genre", methods=["POST"])
def add_genre():
    db = get_db()
    cursor = db.cursor()

    try:
        data = request.get_json()

        # Make sure a genre name was provided
        if not data or not data.get("name"):
            return jsonify({"error": "Genre name is required"}), 400

        name = data["name"]
        description = data.get("description")

        cursor.execute("""
            INSERT INTO genre (name, description)
            VALUES (%s, %s);
        """, (name, description))

        db.commit()

        new_genre_id = cursor.lastrowid

        return jsonify({
            "message": "Genre added successfully",
            "genre_id": new_genre_id,
            "name": name,
            "description": description
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


# LINK MEDIA TO AN EXISTING GENRE
@genres.route("/genre", methods=["PUT"])
def link_media_to_genre():
    db = get_db()
    cursor = db.cursor()

    try:
        data = request.get_json()

        # Make sure both IDs were provided
        if not data or not data.get("media_id") or not data.get("genre_id"):
            return jsonify({
                "error": "media_id and genre_id are required"
            }), 400

        media_id = data["media_id"]
        genre_id = data["genre_id"]

        # Link existing media to existing genre
        cursor.execute("""
            INSERT INTO media_genre (media_id, genre_id)
            VALUES (%s, %s);
        """, (media_id, genre_id))

        db.commit()

        return jsonify({
            "message": "Media linked to genre successfully",
            "media_id": media_id,
            "genre_id": genre_id
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()