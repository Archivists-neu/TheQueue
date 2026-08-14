from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error, IntegrityError


VALID_FRIENDSHIP_STATUSES = {"pending", "accepted", "declined", "blocked"}


# Create a Blueprint for friendship routes
friendships = Blueprint("friendship", __name__)


# GET ALL FRIENDSHIPS
@friendships.route("/friendships", methods=["GET"])
def get_all_friendships():

    cursor = get_db().cursor(dictionary=True)

    try:

        current_app.logger.info(
            "GET /friendship/friendships"
        )

        requester_id = request.args.get(
            "requester_id"
        )

        addressee_id = request.args.get(
            "addressee_id"
        )

        status = request.args.get(
            "status"
        )

        date_requested = request.args.get(
            "date_requested"
        )


        # Join the user table twice.
        # This lets us return the names of both people
        # instead of only their user IDs.
        query = """
            SELECT
                f.friendship_id,
                f.requester_id,
                CONCAT(
                    requester.first_name,
                    ' ',
                    requester.last_name
                ) AS requester_name,

                f.addressee_id,
                CONCAT(
                    addressee.first_name,
                    ' ',
                    addressee.last_name
                ) AS addressee_name,

                f.status,
                f.date_requested,
                f.date_accepted

            FROM friendship f

            JOIN user requester
                ON f.requester_id = requester.user_id

            JOIN user addressee
                ON f.addressee_id = addressee.user_id

            WHERE 1=1
        """

        params = []


        if requester_id:
            query += " AND f.requester_id = %s"
            params.append(requester_id)


        if addressee_id:
            query += " AND f.addressee_id = %s"
            params.append(addressee_id)


        if status:
            query += " AND f.status = %s"
            params.append(status)


        if date_requested:
            query += " AND f.date_requested = %s"
            params.append(date_requested)


        query += " ORDER BY f.date_requested DESC"


        cursor.execute(
            query,
            params
        )

        friendship_list = cursor.fetchall()


        current_app.logger.info(
            f"Retrieved "
            f"{len(friendship_list)} friendships"
        )


        return jsonify(
            friendship_list
        ), 200


    except Error as e:

        current_app.logger.error(
            f"Database error in "
            f"get_all_friendships: {e}"
        )

        return jsonify({
            "error": str(e)
        }), 500


    finally:
        cursor.close()


# SEND A FRIEND REQUEST
@friendships.route("/friendships", methods=["POST"])
def create_friendship():

    cursor = get_db().cursor(dictionary=True)

    try:

        current_app.logger.info("POST /friendship/friendships")

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        for field in ["requester_id", "addressee_id"]:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        requester_id = data["requester_id"]
        addressee_id = data["addressee_id"]

        if requester_id == addressee_id:
            return jsonify({"error": "A user cannot befriend themselves"}), 400

        status = data.get("status", "pending")

        if status not in VALID_FRIENDSHIP_STATUSES:
            return jsonify({
                "error": f"Invalid status. Must be one of: "
                         f"{', '.join(sorted(VALID_FRIENDSHIP_STATUSES))}"
            }), 400

        query = """
            INSERT INTO friendship
                (requester_id, addressee_id, status, date_requested)
            VALUES
                (%s, %s, %s, NOW())
        """

        cursor.execute(query, (requester_id, addressee_id, status))
        get_db().commit()

        new_friendship_id = cursor.lastrowid

        current_app.logger.info(f"Created friendship {new_friendship_id}")

        return jsonify({
            "message": "Friend request sent",
            "friendship_id": new_friendship_id,
            "status": status
        }), 201

    except IntegrityError:
        # (requester_id, addressee_id) is unique, and both are foreign keys.
        get_db().rollback()
        current_app.logger.warning("create_friendship: integrity constraint violated")

        return jsonify({
            "error": "That friendship already exists, or one of the users does not"
        }), 409

    except Error as e:

        get_db().rollback()

        current_app.logger.error(
            f"Database error in create_friendship: {e}"
        )

        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()


# RESPOND TO A FRIEND REQUEST
@friendships.route("/friendships/<int:friendship_id>", methods=["PUT"])
def update_friendship(friendship_id):

    cursor = get_db().cursor(dictionary=True)

    try:

        current_app.logger.info(f"PUT /friendship/friendships/{friendship_id}")

        data = request.get_json(silent=True)

        if not isinstance(data, dict) or "status" not in data:
            return jsonify({"error": "Missing required field: status"}), 400

        status = data["status"]

        if status not in VALID_FRIENDSHIP_STATUSES:
            return jsonify({
                "error": f"Invalid status. Must be one of: "
                         f"{', '.join(sorted(VALID_FRIENDSHIP_STATUSES))}"
            }), 400

        cursor.execute(
            "SELECT friendship_id FROM friendship WHERE friendship_id = %s",
            (friendship_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": f"Friendship with id {friendship_id} not found"
            }), 404

        # Accepting stamps the date; any other outcome clears it.
        if status == "accepted":
            query = """
                UPDATE friendship
                SET status = %s, date_accepted = NOW()
                WHERE friendship_id = %s
            """
        else:
            query = """
                UPDATE friendship
                SET status = %s, date_accepted = NULL
                WHERE friendship_id = %s
            """

        cursor.execute(query, (status, friendship_id))
        get_db().commit()

        current_app.logger.info(
            f"Friendship {friendship_id} set to {status}"
        )

        return jsonify({
            "message": "Friendship updated",
            "friendship_id": friendship_id,
            "status": status
        }), 200

    except Error as e:

        get_db().rollback()

        current_app.logger.error(
            f"Database error in update_friendship: {e}"
        )

        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()