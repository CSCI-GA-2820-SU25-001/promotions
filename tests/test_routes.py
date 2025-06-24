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
TestPromotion API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service import create_app
from service.common import status
from service.models import db, Promotion

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should return the service root info"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Promotions REST API")
        self.assertEqual(data["version"], "1.0")
        self.assertEqual(data["list_endpoint"], "/promotions")

    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = {
            "name": "Flash Sale",
            "promo_type": "PERCENT_OFF",  # valid enum
            "product_id": 123,
            "amount": 25.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
        }

        response = self.client.post("/promotions", json=test_promotion)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check Location header
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)
        print(location)
        self.assertRegex(location, r"/promotions/\d+$")

        # Validate returned promotion
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion["name"])
        self.assertEqual(data["promo_type"], test_promotion["promo_type"])
        self.assertEqual(data["product_id"], test_promotion["product_id"])
        self.assertEqual(data["amount"], test_promotion["amount"])
        self.assertEqual(data["start_date"], test_promotion["start_date"])
        self.assertEqual(data["end_date"], test_promotion["end_date"])

    def test_list_all_promotions(self):
        """It should return a list of all Promotions"""
        # Create 2 promotions first
        promo_1 = {
            "name": "Summer Sale",
            "promo_type": "PERCENT_OFF",
            "product_id": 101,
            "amount": 10.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-15",
        }

        promo_2 = {
            "name": "BOGO Offer",
            "promo_type": "BOGO",
            "product_id": 102,
            "amount": 1.0,
            "start_date": "2025-06-05",
            "end_date": "2025-06-20",
        }

        self.client.post("/promotions", json=promo_1)
        self.client.post("/promotions", json=promo_2)

        # call GET /promotions
        response = self.client.get("/promotions")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    # test to trigger check_content_type error to make the coverage above 95%
    def test_create_promotion_with_wrong_content_type(self):
        """It should return 415 UNSUPPORTED MEDIA TYPE if Content-Type is wrong"""
        test_data = {
            "name": "Flash Sale",
            "promo_type": "PERCENT_OFF",
            "product_id": 101,
            "amount": 20.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
        }

        response = self.client.post(
            "/promotions", data=str(test_data), headers={"Content-Type": "text/plain"}
        )
        self.assertEqual(response.status_code, 415)

    ######################################################################
    #  R / U / D route tests (new)
    ######################################################################
    def _create_sample_promo(self):
        payload = {
            "name": "Sample",
            "promo_type": "PERCENT_OFF",
            "product_id": 1,
            "amount": 5.0,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        }
        resp = self.client.post("/promotions", json=payload)
        return resp.get_json()["id"]

    def test_read_promotion(self):
        pid = self._create_sample_promo()
        resp = self.client.get(f"/promotions/{pid}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["id"], pid)

    def test_update_promotion(self):
        pid = self._create_sample_promo()
        update = {
            "name": "Updated",
            "promo_type": "AMOUNT_OFF",
            "product_id": 2,
            "amount": 9.99,
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
        }
        resp = self.client.put(f"/promotions/{pid}", json=update)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.get_json()["amount"], update["amount"])

    def test_delete_promotion(self):
        pid = self._create_sample_promo()
        resp = self.client.delete(f"/promotions/{pid}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # second delete – idempotent 204
        resp = self.client.delete(f"/promotions/{pid}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
