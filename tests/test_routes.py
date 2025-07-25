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
from service.common import status
from service.models import db, Promotion
from service.common.log_handlers import init_logging

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
        resp = self.client.get("/", headers={"Accept": "application/json"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Promotions REST API")
        self.assertEqual(data["version"], "1.0")
        self.assertEqual(data["list_endpoint"], "/api/promotions")

    def test_create_promotion(self):
        """It should Create a new Promotion"""
        test_promotion = {
            "name": "Flash Sale",
            "promo_type": "PERCENT_OFF",
            "product_id": 123,
            "amount": 25.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
        }

        response = self.client.post("/api/promotions", json=test_promotion)
        print(response)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)
        self.assertRegex(location, r"/api/promotions/\d+$")

        data = response.get_json()
        self.assertEqual(data["name"], test_promotion["name"])
        self.assertEqual(data["promo_type"], test_promotion["promo_type"])
        self.assertEqual(data["product_id"], test_promotion["product_id"])
        self.assertEqual(data["amount"], test_promotion["amount"])
        self.assertEqual(data["start_date"], test_promotion["start_date"])
        self.assertEqual(data["end_date"], test_promotion["end_date"])
        self.assertTrue(data["status"])  # Added status assertion

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

        self.client.post("/api/promotions", json=promo_1)
        self.client.post("/api/promotions", json=promo_2)

        # call GET /api/promotions
        response = self.client.get("/api/promotions")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        self.assertTrue(data[0]["status"])
        self.assertTrue(data[1]["status"])

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
            "/api/promotions",
            data=str(test_data),
            headers={"Content-Type": "text/plain"},
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
        resp = self.client.post("/api/promotions", json=payload)
        return resp.get_json()["id"]

    def test_read_promotion(self):
        """It should retrieve a promotion by ID and return 200 OK."""
        pid = self._create_sample_promo()
        resp = self.client.get(f"/api/promotions/{pid}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], pid)
        self.assertTrue(data["status"])  # Added

    def test_update_with_wrong_content_type(self):
        """It should return 415 when Content-Type is not application/json."""
        pid = self._create_sample_promo()
        update = {
            "name": "Updated Promo",
            "promo_type": "AMOUNT_OFF",
            "product_id": 2,
            "amount": 9.99,
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
        }
        response = self.client.put(
            f"/api/promotions/{pid}",
            data=str(update),
            headers={"Content-Type": "text/plain"},
        )
        self.assertEqual(response.status_code, 415)

    def test_update_with_mismatched_id(self):
        """It should return 400 when IDs in URL and body don't match."""
        pid = self._create_sample_promo()
        update = {
            "id": pid + 1000,  # Force mismatch
            "name": "Mismatch Promo",
            "promo_type": "AMOUNT_OFF",
            "product_id": 2,
            "amount": 9.99,
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
        }
        response = self.client.put(f"/api/promotions/{pid}", json=update)
        self.assertEqual(response.status_code, 400)

    def test_update_returns_updated_promotion(self):
        """It should return the updated promotion successfully."""
        pid = self._create_sample_promo()
        update = {
            "name": "FinalCheck",
            "promo_type": "PERCENT_OFF",
            "product_id": 123,
            "amount": 30.0,
            "start_date": "2025-07-01",
            "end_date": "2025-07-31",
        }
        response = self.client.put(f"/api/promotions/{pid}", json=update)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["name"], "FinalCheck")
        self.assertTrue(data["status"])  # Added

    def test_update_promotion(self):
        """It should update an existing promotion and return the updated data."""
        pid = self._create_sample_promo()
        update = {
            "name": "Updated",
            "promo_type": "AMOUNT_OFF",
            "product_id": 2,
            "amount": 9.99,
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
        }
        resp = self.client.put(f"/api/promotions/{pid}", json=update)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["amount"], update["amount"])
        self.assertTrue(data["status"])  # Added

    def test_delete_promotion(self):
        """It should delete a promotion successfully."""
        pid = self._create_sample_promo()
        resp = self.client.delete(f"/api/promotions/{pid}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # second delete – idempotent 204
        resp = self.client.delete(f"/api/promotions/{pid}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_nonexistent_promotion(self):
        """It should return 404 when updating a non-existent promotion."""
        update_data = {
            "name": "Invalid Promo",
            "product_id": 999,
            "promo_type": "bogo",
            "amount": 5,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        response = self.client.put(
            "/api/promotions/999", json=update_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_nonexistent_promotion(self):
        """It should return 404 when getting a non-existent promotion."""
        response = self.client.get("/api/promotions/999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_promotions_with_id_query(self):
        """It should return a specific promotion when queried by ID"""
        promo = {
            "name": "Targeted Promo",
            "promo_type": "PERCENT_OFF",
            "product_id": 200,
            "amount": 20.0,
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
        }

        create_resp = self.client.post("/api/promotions", json=promo)
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        created_data = create_resp.get_json()
        created_id = created_data["id"]

        query_resp = self.client.get(f"/api/promotions?id={created_id}")
        self.assertEqual(query_resp.status_code, status.HTTP_200_OK)

        data = query_resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], created_id)
        self.assertEqual(data[0]["name"], "Targeted Promo")
        self.assertTrue(data[0]["status"])  # Added

    def test_activate_promotion_put(self):
        """It should activate a promotion using PUT and return 200 OK"""
        pid = self._create_sample_promo()

        # Set to inactive first
        self.client.delete(f"/api/promotions/{pid}/deactivate")

        # Now activate using PUT
        resp = self.client.put(f"/api/promotions/{pid}/activate")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["message"], f"Promotion {pid} activated")
        self.assertTrue(data["status"])

    def test_deactivate_promotion(self):
        """It should deactivate a promotion and set status=False"""
        pid = self._create_sample_promo()

        # Deactivate
        resp = self.client.delete(f"/api/promotions/{pid}/deactivate")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertFalse(data["status"])

    def test_list_promotions_with_invalid_id(self):
        """It should return 400 for non-integer id query"""
        resp = self.client.get("/api/promotions?id=abc")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_promotions_with_nonexistent_id(self):
        """It should return 404 when queried with a non-existent id"""
        resp = self.client.get("/api/promotions?id=9999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """It should return 405 METHOD NOT ALLOWED for invalid methods."""
        resp = self.client.put("/")  # Root doesn't allow PUT
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_not_acceptable(self):
        """It should return 406 NOT ACCEPTABLE for unsupported Accept headers."""
        resp = self.client.get("/", headers={"Accept": "application/xml"})
        self.assertEqual(resp.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_unsupported_media_type(self):
        """It should return 415 UNSUPPORTED MEDIA TYPE for invalid Content-Type."""
        resp = self.client.post(
            "/api/promotions", data="{}", headers={"Content-Type": "text/xml"}
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_logging_handler_setup(self):
        """It should initialize the logging handler properly."""
        init_logging(app, "gunicorn.error")

    def test_health_check_endpoint(self):
        """It should return health status OK"""
        resp = self.client.get("/api/promotions/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_activate_nonexistent_promotion(self):
        """It should return 404 when activating a non-existent promotion"""
        resp = self.client.put("/api/promotions/9999/activate")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_nonexistent_promotion(self):
        """It should return 404 when deactivating a non-existent promotion"""
        resp = self.client.delete("/api/promotions/9999/deactivate")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_promotion_with_invalid_json(self):
        """It should return 400 for malformed JSON"""
        resp = self.client.post(
            "/api/promotions",
            data="{invalid json}",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_missing_required_fields(self):
        """It should return 400 for missing required fields"""
        incomplete_data = {
            "name": "Incomplete Promo",
            # Missing promo_type, product_id, amount, start_date, end_date
        }
        resp = self.client.post("/api/promotions", json=incomplete_data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_promotion_with_invalid_json(self):
        """It should return 400 for malformed JSON in update"""
        pid = self._create_sample_promo()
        resp = self.client.put(
            f"/api/promotions/{pid}",
            data="{invalid json}",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_promotion_with_wrong_content_type_text(self):
        """It should return 415 for wrong content type on create"""
        promo_data = {
            "name": "Test Promo",
            "promo_type": "PERCENT_OFF",
            "product_id": 1,
            "amount": 10.0,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        }
        resp = self.client.post(
            "/api/promotions", json=promo_data, headers={"Content-Type": "text/plain"}
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_promotion_with_wrong_content_type(self):
        """It should return 415 for wrong content type on update"""
        pid = self._create_sample_promo()
        update_data = {
            "name": "Updated Promo",
            "promo_type": "AMOUNT_OFF",
            "product_id": 2,
            "amount": 5.0,
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
        }
        resp = self.client.put(
            f"/api/promotions/{pid}",
            json=update_data,
            headers={"Content-Type": "text/xml"},
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_promotion_with_string_id(self):
        """It should handle string IDs gracefully"""
        resp = self.client.get("/api/promotions/abc")
        # Flask-RESTX should handle this and return 404
        self.assertIn(
            resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
        )

    def test_update_promotion_with_string_id(self):
        """It should handle string IDs gracefully in update"""
        update_data = {
            "name": "Test Update",
            "promo_type": "PERCENT_OFF",
            "product_id": 1,
            "amount": 15.0,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        }
        resp = self.client.put("/api/promotions/abc", json=update_data)
        # Flask-RESTX should handle this and return 404
        self.assertIn(
            resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
        )

    def test_delete_promotion_with_string_id(self):
        """It should handle string IDs gracefully in delete"""
        resp = self.client.delete("/api/promotions/abc")
        # Flask-RESTX should handle this and return 404
        self.assertIn(
            resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
        )

    def test_activate_promotion_with_string_id(self):
        """It should handle string IDs gracefully in activate"""
        resp = self.client.put("/api/promotions/abc/activate")
        # Flask-RESTX should handle this and return 404
        self.assertIn(
            resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
        )

    def test_deactivate_promotion_with_string_id(self):
        """It should handle string IDs gracefully in deactivate"""
        resp = self.client.delete("/api/promotions/abc/deactivate")
        # Flask-RESTX should handle this and return 404
        self.assertIn(
            resp.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
        )

    def test_create_promotion_with_additional_fields(self):
        """It should handle creation with additional fields that are ignored"""
        promo_data = {
            "name": "Test Promo with Extra",
            "promo_type": "PERCENT_OFF",
            "product_id": 1,
            "amount": 10.0,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "extra_field": "should be ignored",
            "another_extra": 999,
        }
        resp = self.client.post("/api/promotions", json=promo_data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["name"], "Test Promo with Extra")
        self.assertNotIn("extra_field", data)
        self.assertNotIn("another_extra", data)

    def test_update_promotion_preserve_id(self):
        """It should preserve the promotion ID during update"""
        pid = self._create_sample_promo()
        update_data = {
            "id": pid,  # Include the correct ID
            "name": "ID Preserved Update",
            "promo_type": "AMOUNT_OFF",
            "product_id": 3,
            "amount": 7.5,
            "start_date": "2025-03-01",
            "end_date": "2025-03-31",
        }
        resp = self.client.put(f"/api/promotions/{pid}", json=update_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], pid)
        self.assertEqual(data["name"], "ID Preserved Update")

    def test_list_promotions_empty_database(self):
        """It should return empty list when no promotions exist"""
        # Clear all promotions first
        promotions = Promotion.all()
        for promotion in promotions:
            promotion.delete()

        resp = self.client.get("/api/promotions")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    def test_multiple_promotions_list(self):
        """It should return multiple promotions when they exist"""
        # Create multiple promotions
        promo1 = {
            "name": "First Promo",
            "promo_type": "PERCENT_OFF",
            "product_id": 1,
            "amount": 10.0,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        }
        promo2 = {
            "name": "Second Promo",
            "promo_type": "BOGO",
            "product_id": 2,
            "amount": 1.0,
            "start_date": "2025-02-01",
            "end_date": "2025-02-28",
        }
        promo3 = {
            "name": "Third Promo",
            "promo_type": "AMOUNT_OFF",
            "product_id": 3,
            "amount": 5.0,
            "start_date": "2025-03-01",
            "end_date": "2025-03-31",
        }

        self.client.post("/api/promotions", json=promo1)
        self.client.post("/api/promotions", json=promo2)
        self.client.post("/api/promotions", json=promo3)

        resp = self.client.get("/api/promotions")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 3)

    def test_promotion_status_defaults_to_true(self):
        """It should set promotion status to True by default on creation"""
        promo_data = {
            "name": "Default Status Promo",
            "promo_type": "PERCENT_OFF",
            "product_id": 1,
            "amount": 15.0,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
        }
        resp = self.client.post("/api/promotions", json=promo_data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertTrue(data["status"])  # Should default to True
