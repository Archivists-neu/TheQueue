from flask import Blueprint, request, jsonify
from backend.db_connection import get_db


# Location Blueprint
locations = Blueprint("locations", __name__)


# GET ALL LOCATIONS
@locations.route("/", methods=["GET"])
def get_locations():
    """
    Every location, sorted the way a person reads them.

    The sign-up form shows these as "City, State" and posts back the
    location_id, so the user never has to know the id exists.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT location_id, city, state, country
            FROM location
            ORDER BY country, state, city;
        """)

        location_list = cursor.fetchall()

        return jsonify(location_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


# ADD NEW LOCATION
@locations.route("/", methods=["POST"])
def add_location():
    """
    Create a location, or hand back the id of the matching one.

    The table has no unique key on city/state/country, so a plain insert
    would quietly pile up duplicate "Boston, Massachusetts" rows.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        data = request.get_json()

        if not data or not data.get("city"):
            return jsonify({"error": "city is required"}), 400

        city = data["city"]
        state = data.get("state")
        country = data.get("country") or "United States"

        cursor.execute("""
            SELECT location_id
            FROM location
            WHERE city = %s
              AND (state = %s OR (state IS NULL AND %s IS NULL))
              AND country = %s;
        """, (city, state, state, country))

        existing = cursor.fetchone()

        if existing:
            return jsonify({
                "message": "Location already exists",
                "location_id": existing["location_id"],
                "city": city,
                "state": state,
                "country": country
            }), 200

        cursor.execute("""
            INSERT INTO location (city, state, country)
            VALUES (%s, %s, %s);
        """, (city, state, country))

        db.commit()

        return jsonify({
            "message": "Location added successfully",
            "location_id": cursor.lastrowid,
            "city": city,
            "state": state,
            "country": country
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
