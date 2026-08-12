from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error

reviews = Blueprint("reviews", __name__)

# Get all reviews with optional filtering by user, media, date, likes, or comment
@reviews.route("/reviews", methods=["GET"])
def get_all_reviews():
    cursor = get_db().cursor(dictionary=True)
    try:
        current_app.logger.info('GET /reviews')
        user_id = request.args.get("user_id")
        media_id = request.args.get("media_id")
        review_date = request.args.get("review_date")
        likes = request.args.get("likes")
        review_comment = request.args.get("review_comment")
        query = "SELECT * FROM review WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)
        if media_id:
            query += " AND media_id = %s"
            params.append(media_id)
        if review_date:
            query += " AND review_date = %s"
            params.append(review_date)
        if likes:
            query += " AND likes = %s"
            params.append(likes)
        if review_comment:
            query += " AND review_comment = %s"
            params.append(review_comment)

        cursor.execute(query, params)
        review_list = cursor.fetchall()

        current_app.logger.info(f'Retrieved {len(review_list)} reviews')
        return jsonify(review_list), 200
    except Error as e:
        current_app.logger.error(f'Database error in get_all_reviews: {e}')
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Get one specific review
@reviews.route("/reviews/<int:review_id>", methods=["GET"])
def get_review(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM review WHERE review_id = %s",(review_id,))
        review = cursor.fetchone()

        if not review:
            return jsonify({"error": "Review not found"}), 404

        return jsonify(review), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Get a user's review history
@reviews.route("/users/<int:user_id>/reviews", methods=["GET"])
def get_user_reviews(user_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM review WHERE user_id = %s ORDER BY review_date DESC",(user_id,))
        review_history = cursor.fetchall()

        return jsonify(review_history), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Create a new review
@reviews.route("/reviews", methods=["POST"])
def create_review():
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        required_fields = ["review_comment","user_id","media_id"]

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        query = """
            INSERT INTO review
                (review_comment, likes, review_date, user_id, media_id)
            VALUES
                (%s, %s, NOW(), %s, %s)
        """
        cursor.execute(query, (
            data["review_comment"],
            data.get("likes", 0),
            data["user_id"],
            data["media_id"]
        ))
        get_db().commit()

        return jsonify({
            "message": "Review created successfully",
            "review_id": cursor.lastrowid
        }), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Update a specific review
@reviews.route("/reviews/<int:review_id>", methods=["PUT"])
def update_review(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        data = request.get_json()
        cursor.execute("SELECT review_id FROM review WHERE review_id = %s",(review_id,))

        if not cursor.fetchone():
            return jsonify({"error": "Review not found"}), 404

        allowed_fields = ["review_comment","likes"]
        update_fields = [f"{field} = %s"
            for field in allowed_fields
            if field in data]
        params = [data[field]
            for field in allowed_fields
            if field in data]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        params.append(review_id)
        query = f"UPDATE review SET {', '.join(update_fields)} WHERE review_id = %s"
        cursor.execute(query, params)
        get_db().commit()

        return jsonify({"message": "Review updated successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


# Delete/moderate a specific review
@reviews.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):
    cursor = get_db().cursor(dictionary=True)
    try:
        cursor.execute("SELECT review_id FROM review WHERE review_id = %s",(review_id,))

        if not cursor.fetchone():
            return jsonify({"error": "Review not found"}), 404

        cursor.execute("DELETE FROM review WHERE review_id = %s",(review_id,))
        get_db().commit()

        return jsonify({"message": "Review deleted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()