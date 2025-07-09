######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
YourResourceModel Service
This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Promotion
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Handles the index (root) endpoint response."""
    if not request.accept_mimetypes.accept_json:
        return "", status.HTTP_406_NOT_ACCEPTABLE

    return (
        jsonify(
            {
                "name": "Promotions REST API",
                "version": "1.0",
                "list_endpoint": "/promotions",
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW PROMOTION
######################################################################
@app.route("/promotions", methods=["POST"])
def create_promotions():
    """
    Create a Promotion
    """
    app.logger.info("Request to create a Promotion...")
    check_content_type("application/json")

    promotion = Promotion()
    # get data from the request and deserialization
    data = request.get_json()
    app.logger.debug("processing = %s", data)
    promotion.deserialize(data)
    promotion.create()
    app.logger.info("promotion with new id [%s] saved!", promotion.id)
    # umcomment when list all promotion and can read by id is done
    location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)
    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST ALL PROMOTION
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the promotions or filters by query parameters"""
    app.logger.info("Request to list promotions")

    promotion_id = request.args.get("id")

    if promotion_id:
        app.logger.info("Filtering promotions by id=%s", promotion_id)
        try:
            promotion = Promotion.find(int(promotion_id))
        except ValueError:
            abort(status.HTTP_400_BAD_REQUEST, "ID must be an integer.")

        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        return jsonify([promotion.serialize()]), status.HTTP_200_OK

    # If no filter, return all
    promotions = Promotion.all()
    results = [p.serialize() for p in promotions]
    return jsonify(results), status.HTTP_200_OK


######################################################################
# HELPER FUNCTION
######################################################################
def check_content_type(expected_type):
    """Checks that the Content-Type is as expected"""
    content_type = request.headers.get("Content-Type")
    if content_type != expected_type:
        app.logger.error("Invalid Content-Type: %s", content_type)
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {expected_type}",
        )


######################################################################
# READ A PROMOTION BY ID
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
    """Return a single Promotion by its ID"""
    app.logger.info("Request for Promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotion(promotion_id):
    """Update an existing Promotion"""
    app.logger.info("Request to update Promotion with id: %s", promotion_id)
    check_content_type("application/json")

    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    data = request.get_json()
    # If the body contains an id, make sure it matches the path
    if "id" in data and data["id"] != promotion_id:
        abort(
            status.HTTP_400_BAD_REQUEST,
            "The id in the request body does not match the resource path.",
        )

    promotion.deserialize(data)
    promotion.id = promotion_id  # preserve correct id
    promotion.update()

    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotion(promotion_id):
    """Delete a Promotion by its ID"""
    app.logger.info("Request to delete Promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)

    # RFC-conformant: DELETE is idempotent—return 204 even if nothing to delete
    if promotion:
        promotion.delete()

    return "", status.HTTP_204_NO_CONTENT

#####################################################################
# ACTIVATE A PROMOTION
######################################################################
@app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
def activate_promotion(promotion_id):
    """Activate a Promotion by setting status=True"""
    app.logger.info("Request to activate Promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)

    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.status = True
    promotion.update()
    return (
        jsonify(message=f"Promotion {promotion_id} activated", status=promotion.status),
        status.HTTP_200_OK,
    )


######################################################################
# DEACTIVATE A PROMOTION (Soft Delete)
######################################################################
@app.route("/promotions/<int:promotion_id>/deactivate", methods=["DELETE"])
def deactivate_promotion(promotion_id):
    """Deactivate a Promotion by setting status=False"""
    app.logger.info("Request to deactivate Promotion with id: %s", promotion_id)
    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.status = False
    promotion.update()
    return jsonify(promotion.serialize()), status.HTTP_200_OK

######################################################################
# HEALTH CHECK
######################################################################
@app.route("/promotions/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(status="OK"), status.HTTP_200_OK
