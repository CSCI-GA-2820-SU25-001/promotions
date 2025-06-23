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
    """Root endpoint for the Promotions service"""
    return (
        jsonify({
            "name": "Promotions REST API",
            "version": "1.0",
            "list_endpoint": "/promotions"
        }),
        status.HTTP_200_OK
    )
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
    #get data from the request and deserialization
    data = request.get_json()
    app.logger.debug("processing = %s", data)
    promotion.deserialize(data)
    promotion.create()
    app.logger.info("promotion with new id [%s] saved!", promotion.id)
    #umcomment when list all promotion and can read by id is done
    #location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)
    location_url = "unknown"
    return (
        jsonify(promotion.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url}
    )

######################################################################
# LIST ALL PROMOTION
######################################################################
@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the promotions"""
    app.logger.info("Request to list all promotions")

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
            f"Content-Type must be {expected_type}"
        )
######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...
