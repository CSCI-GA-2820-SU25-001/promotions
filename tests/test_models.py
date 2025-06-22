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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import YourResourceModel, DataValidationError, db
from .factories import YourResourceModelFactory
from datetime import date

from service.models import Promotion, PromoType

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  YourResourceModel   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceModel(TestCase):
    """Test Cases for YourResourceModel Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(YourResourceModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_example_replace_this(self):
        """It should create a YourResourceModel"""
        # Todo: Remove this test case example
        resource = YourResourceModelFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = YourResourceModel.all()
        self.assertEqual(len(found), 1)
        data = YourResourceModel.find(resource.id)
        self.assertEqual(data.name, resource.name)

    # Todo: Add your test cases here...


class TestPromotionModel(TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion(self):
        """It should create a Promotion"""
        promo = Promotion(
            name="Summer Sale",
            promo_type=PromoType.PERCENT_OFF.name,
            product_id=1001,
            amount=10.0,
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 30),
        )
        promo.create()
        self.assertIsNotNone(promo.id)
        results = Promotion.all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Summer Sale")

    def test_update_a_promotion(self):
        """It should update a Promotion"""
        promo = Promotion(
            name="Winter Sale",
            promo_type=PromoType.AMOUNT_OFF.name,
            product_id=1002,
            amount=5.0,
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 31),
        )
        promo.create()
        promo.amount = 8.0
        promo.update()
        updated = Promotion.find(promo.id)
        self.assertEqual(updated.amount, 8.0)

    def test_delete_a_promotion(self):
        """It should delete a Promotion"""
        promo = Promotion(
            name="Flash Deal",
            promo_type=PromoType.BOGO.name,
            product_id=1003,
            amount=1.0,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 7, 15),
        )
        promo.create()
        promo_id = promo.id
        promo.delete()
        self.assertIsNone(Promotion.find(promo_id))

    def test_serialize_a_promotion(self):
        """It should serialize a Promotion into a dictionary"""
        promo = Promotion(
            name="Cyber Week",
            promo_type=PromoType.PERCENT_OFF.name,
            product_id=1004,
            amount=25.0,
            start_date=date(2025, 11, 25),
            end_date=date(2025, 12, 1),
        )
        result = promo.serialize()
        self.assertEqual(result["name"], "Cyber Week")
        self.assertEqual(result["promo_type"], "PERCENT_OFF")

    def test_deserialize_a_promotion(self):
        """It should deserialize a dictionary into a Promotion"""
        data = {
            "name": "Back to School",
            "promo_type": "AMOUNT_OFF",
            "product_id": 1005,
            "amount": 7.0,
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
        }
        promo = Promotion()
        promo.deserialize(data)
        self.assertEqual(promo.name, "Back to School")
        self.assertEqual(promo.promo_type, "AMOUNT_OFF")

    def test_find_by_name(self):
        """It should find promotions by name"""
        promo = Promotion(
            name="Mega Discount",
            promo_type=PromoType.AMOUNT_OFF.name,
            product_id=1006,
            amount=12.0,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 30),
        )
        promo.create()
        results = Promotion.find_by_name("Mega Discount")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].product_id, 1006)

    def test_deserialize_with_bad_data(self):
        """It should raise a DataValidationError for bad promo_type"""
        bad_data = {
            "name": "Invalid",
            "promo_type": "INVALID_TYPE",
            "product_id": 1007,
            "amount": 5.0,
            "start_date": "2025-09-01",
            "end_date": "2025-09-30",
        }
        promo = Promotion()
        with self.assertRaises(DataValidationError):
            promo.deserialize(bad_data)
