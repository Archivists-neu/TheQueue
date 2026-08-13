from flask import Blueprint, jsonify, request, current_app
from backend.db_connection import get_db
from mysql.connector import Error


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