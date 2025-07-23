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
Promotion Steps

Steps file for promotions.feature

This handles the background setup:
  Given the following promotions
"""

import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following promotions exist")
def step_impl(context):
    """Delete all promotions and load new ones"""

    rest_endpoint = f"{context.base_url}/api/promotions"

    # Get all existing promotions
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    for promotion in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{promotion['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load new promotions from scenario table
    for row in context.table:
        status = row["Status"].strip().lower() == "true"
        payload = {
            "name": row["Name"],
            "promo_type": row["Type"],
            "product_id": int(row["Product ID"]),
            "amount": float(row["Amount"]),
            "start_date": row["Start Date"],
            "end_date": row["End Date"],
            "status": status,
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
