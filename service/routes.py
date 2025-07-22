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
Promotions Service
This service implements a REST API that allows you to Create, Read, Update
and Delete Promotions using Flask-RESTX
"""
import os
from flask import request
from flask import current_app as app  # Import Flask application
from flask import send_from_directory, abort
from flask_restx import Resource, fields, Namespace
from service.models import Promotion
from service.common import status  # HTTP Status Codes

# Get the API instance from app extensions
api = app.extensions.get("promotions_api")

# Define the promotion namespace
ns = Namespace("promotions", description="Promotion operations")
if api:
    api.add_namespace(ns)

# Define the promotion model for Swagger documentation
promotion_model = ns.model(
    "Promotion",
    {
        "id": fields.Integer(
            readOnly=True, description="The promotion unique identifier"
        ),
        "name": fields.String(required=True, description="The promotion name"),
        "promo_type": fields.String(
            required=True,
            description="The promotion type (PERCENT_OFF, BOGO, AMOUNT_OFF)",
        ),
        "product_id": fields.Integer(
            required=True, description="The product identifier"
        ),
        "amount": fields.Float(required=True, description="The discount amount"),
        "start_date": fields.String(
            required=True, description="The start date (YYYY-MM-DD)"
        ),
        "end_date": fields.String(
            required=True, description="The end date (YYYY-MM-DD)"
        ),
        "status": fields.Boolean(readOnly=True, description="The promotion status"),
    },
)

create_model = ns.model(
    "PromotionCreate",
    {
        "name": fields.String(required=True, description="The promotion name"),
        "promo_type": fields.String(
            required=True,
            description="The promotion type (PERCENT_OFF, BOGO, AMOUNT_OFF)",
        ),
        "product_id": fields.Integer(
            required=True, description="The product identifier"
        ),
        "amount": fields.Float(required=True, description="The discount amount"),
        "start_date": fields.String(
            required=True, description="The start date (YYYY-MM-DD)"
        ),
        "end_date": fields.String(
            required=True, description="The end date (YYYY-MM-DD)"
        ),
    },
)


######################################################################
# HELPER FUNCTION
######################################################################
def check_content_type(expected_type):
    """Checks that the Content-Type is as expected"""
    content_type = request.headers.get("Content-Type")
    if content_type != expected_type:
        app.logger.error("Invalid Content-Type: %s", content_type)
        ns.abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {expected_type}",
        )

@app.before_request
def check_accept_header():
    if not request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        abort(status.HTTP_406_NOT_ACCEPTABLE, description="Not Acceptable: Only 'application/json' or 'text/html' is supported.")

######################################################################
# ROOT ENDPOINT (Serve index.html)
######################################################################
@app.route("/", methods=["GET"])
def index():
    """Serve UI index.html for browsers, JSON for API clients"""
    if request.accept_mimetypes.accept_html:
        static_path = os.path.join(app.root_path, "static")
        return send_from_directory(static_path, "index.html")
    return {
        "name": "Promotions REST API",
        "version": "1.0",
        "list_endpoint": "/api/promotions",
    }, status.HTTP_200_OK


######################################################################
# PROMOTION COLLECTION RESOURCE
######################################################################
@ns.route("")
class PromotionCollection(Resource):
    """Handles all interactions with collections of Promotions"""

    @ns.doc("list_promotions")
    @ns.marshal_list_with(promotion_model)
    def get(self):
        """Fetch all Promotions"""
        app.logger.info("Request to list promotions")

        promotion_id = request.args.get("id")

        if promotion_id:
            app.logger.info("Filtering promotions by id=%s", promotion_id)
            try:
                promotion = Promotion.find(int(promotion_id))
            except ValueError:
                ns.abort(status.HTTP_400_BAD_REQUEST, "ID must be an integer.")

            if not promotion:
                ns.abort(
                    status.HTTP_404_NOT_FOUND,
                    f"Promotion with id '{promotion_id}' was not found.",
                )
            return [promotion.serialize()], status.HTTP_200_OK

        # If no filter, return all
        promotions = Promotion.all()
        results = [p.serialize() for p in promotions]
        return results, status.HTTP_200_OK

    @ns.doc("create_promotion")
    @ns.expect(create_model)
    @ns.marshal_with(promotion_model, code=201)
    def post(self):
        """Create a new Promotion"""
        app.logger.info("Request to create a Promotion...")
        check_content_type("application/json")

        promotion = Promotion()
        # get data from the request and deserialization
        data = request.get_json()
        app.logger.debug("processing = %s", data)
        promotion.deserialize(data)
        promotion.create()
        app.logger.info("promotion with new id [%s] saved!", promotion.id)

        return (
            promotion.serialize(),
            status.HTTP_201_CREATED,
            {
                "Location": api.url_for(
                    PromotionResource, promotion_id=promotion.id, _external=True
                )
            },
        )


######################################################################
# PROMOTION RESOURCE
######################################################################
@ns.route("/<int:promotion_id>")
@ns.param("promotion_id", "The Promotion identifier")
class PromotionResource(Resource):
    """Handles all interactions with a single Promotion"""

    @ns.doc("get_promotion")
    @ns.marshal_with(promotion_model)
    def get(self, promotion_id):
        """Fetch a Promotion"""
        app.logger.info("Request for Promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )
        return promotion.serialize(), status.HTTP_200_OK

    @ns.doc("update_promotion")
    @ns.expect(promotion_model)
    @ns.marshal_with(promotion_model)
    def put(self, promotion_id):
        """Update a Promotion"""
        app.logger.info("Request to update Promotion with id: %s", promotion_id)
        check_content_type("application/json")

        promotion = Promotion.find(promotion_id)
        if not promotion:
            ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        data = request.get_json()
        # If the body contains an id, make sure it matches the path
        if "id" in data and data["id"] != promotion_id:
            ns.abort(
                status.HTTP_400_BAD_REQUEST,
                "The id in the request body does not match the resource path.",
            )

        promotion.deserialize(data)
        promotion.id = promotion_id  # preserve correct id
        promotion.update()

        return promotion.serialize(), status.HTTP_200_OK

    @ns.doc("delete_promotion")
    def delete(self, promotion_id):
        """Delete a Promotion"""
        app.logger.info("Request to delete Promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)

        # RFC-conformant: DELETE is idempotent—return 204 even if nothing to delete
        if promotion:
            promotion.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# PROMOTION ACTION RESOURCES
######################################################################
@ns.route("/<int:promotion_id>/activate")
@ns.param("promotion_id", "The Promotion identifier")
class ActivatePromotionResource(Resource):
    """Activate a Promotion"""

    @ns.doc("activate_promotion")
    def put(self, promotion_id):
        """Activate a Promotion by setting status=True"""
        app.logger.info("Request to activate Promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)

        if not promotion:
            ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        promotion.status = True
        promotion.update()
        return {
            "message": f"Promotion {promotion_id} activated",
            "status": promotion.status,
        }, status.HTTP_200_OK


@ns.route("/<int:promotion_id>/deactivate")
@ns.param("promotion_id", "The Promotion identifier")
class DeactivatePromotionResource(Resource):
    """Deactivate a Promotion"""

    @ns.doc("deactivate_promotion")
    def delete(self, promotion_id):
        """Deactivate a Promotion by setting status=False"""
        app.logger.info("Request to deactivate Promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            ns.abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        promotion.status = False
        promotion.update()
        return promotion.serialize(), status.HTTP_200_OK


@ns.route("/health")
class HealthCheckResource(Resource):
    """Health check endpoint"""

    @ns.doc("health_check")
    def get(self):
        """Health check endpoint"""
        return {"status": "OK"}, status.HTTP_200_OK
