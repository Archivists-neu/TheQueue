from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

recommendations = Blueprint("recommendations", __name__)

# Get all recommendations with optional filtering by friendship, media, and recommendation date
@recommendations.route("", methods=["GET"])
@recommendations.route("/", methods=["GET"])
def get_all_recommendations():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info("GET /recommendations")
        friendship_id = request.args.get("friendship_id")
        media_id = request.args.get("media_id")
        recommendation_date = request.args.get("recommendation_date")
        query = "SELECT * FROM recommendation WHERE 1=1"
        params = []

        if friendship_id:
            query += " AND friendship_id = %s"
            params.append(friendship_id)
        if media_id:
            query += " AND media_id = %s"
            params.append(media_id)
        if recommendation_date:
            query += " AND recommendation_date = %s"
            params.append(recommendation_date)

        query += " ORDER BY recommendation_date DESC"
        cursor.execute(query, params)
        recommendation_list = cursor.fetchall()

        current_app.logger.info(f"Retrieved {len(recommendation_list)} recommendations")
        return jsonify(recommendation_list), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_all_recommendations: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Get one specific recommendation
@recommendations.route("/<int:recommendation_id>", methods=["GET"])
def get_recommendation(recommendation_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM recommendation WHERE recommendation_id = %s",(recommendation_id,))
        recommendation = cursor.fetchone()

        if not recommendation:
            return jsonify({"error": "Recommendation not found"}), 404

        return jsonify(recommendation), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_recommendation: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Get all recommendations associated with a user
@recommendations.route("/users/<int:user_id>/recommendations", methods=["GET"])
def get_user_recommendations(user_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        query = """
            SELECT r.*
            FROM recommendation r
            JOIN friendship f
                ON r.friendship_id = f.friendship_id
            WHERE f.requester_id = %s
               OR f.addressee_id = %s
            ORDER BY r.recommendation_date DESC
        """

        cursor.execute(query, (user_id, user_id))
        user_recommendations = cursor.fetchall()
        current_app.logger.info(f"Retrieved {len(user_recommendations)} "f"recommendations for user {user_id}")

        return jsonify(user_recommendations), 200
    except Error as e:
        current_app.logger.error(f"Database error in get_user_recommendations: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Create a new recommendation to a friend
@recommendations.route("", methods=["POST"])
@recommendations.route("/", methods=["POST"])
def create_recommendation():
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        required_fields = ["friendship_id","media_id"]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """
            INSERT INTO recommendation
                (
                    recommendation_date,
                    attached_message,
                    friendship_id,
                    media_id
                )
            VALUES
                (NOW(), %s, %s, %s)
        """
        cursor.execute(query, (data.get("attached_message"),data["friendship_id"],data["media_id"]))
        get_db().commit()

        return jsonify({"message": "Recommendation created successfully","recommendation_id": cursor.lastrowid}), 201
    except Error as e:
        current_app.logger.error(f"Database error in create_recommendation: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Update an existing recommendation
@recommendations.route("/<int:recommendation_id>", methods=["PUT"])
def update_recommendation(recommendation_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        cursor.execute("SELECT recommendation_id FROM recommendation WHERE recommendation_id = %s",(recommendation_id,))

        if not cursor.fetchone():
            return jsonify({"error": "Recommendation not found"}), 404

        allowed_fields = ["attached_message","media_id"]
        update_fields = [f"{field} = %s" for field in allowed_fields if field in data]
        params = [data[field] for field in allowed_fields if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(recommendation_id)
        query = f"UPDATE recommendation SET {', '.join(update_fields)} WHERE recommendation_id = %s"
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Recommendation updated successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in update_recommendation: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Delete an outdated recommendation
@recommendations.route("/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendation(recommendation_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT recommendation_id FROM recommendation WHERE recommendation_id = %s",(recommendation_id,))

        if not cursor.fetchone():
            return jsonify({"error": "Recommendation not found"}), 404

        cursor.execute("DELETE FROM recommendation WHERE recommendation_id = %s",(recommendation_id,))
        get_db().commit()

        return jsonify({"message": "Recommendation deleted successfully"}), 200
    except Error as e:
        current_app.logger.error(f"Database error in delete_recommendation: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
