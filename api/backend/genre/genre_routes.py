from flask import Blueprint, request, jsonify
from backend.db_connection import get_db

# Genre Blueprint
genres = Blueprint("genres", __name__)


# GET ALL GENRES
@genres.route("/genre", methods=["GET"])
def get_genres():
    cursor = get_db().cursor(dictionary=True)

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
    cursor = get_db().cursor()

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

        get_db().commit()

        new_genre_id = cursor.lastrowid

        return jsonify({
            "message": "Genre added successfully",
            "genre_id": new_genre_id,
            "name": name,
            "description": description
        }), 201

    except Exception as e:
        get_db().rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        