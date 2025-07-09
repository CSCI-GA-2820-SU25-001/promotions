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
import logging
import os
from datetime import date
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import DataValidationError, PromoType, Promotion, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


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
            status=True,
        )
        promo.create()
        self.assertIsNotNone(promo.id)
        results = Promotion.all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Summer Sale")
        self.assertTrue(results[0].status)

    def test_update_a_promotion(self):
        """It should update a Promotion"""
        promo = Promotion(
            name="Winter Sale",
            promo_type=PromoType.AMOUNT_OFF.name,
            product_id=1002,
            amount=5.0,
            start_date=date(2025, 12, 1),
            end_date=date(2025, 12, 31),
            status=True,
        )
        promo.create()
        promo.amount = 8.0
        promo.status = False
        promo.update()
        updated = Promotion.find(promo.id)
        self.assertEqual(updated.amount, 8.0)
        self.assertFalse(updated.status)

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
            status=False,
        )
        result = promo.serialize()
        self.assertEqual(result["name"], "Cyber Week")
        self.assertEqual(result["promo_type"], "PERCENT_OFF")
        self.assertFalse(result["status"])

    def test_deserialize_a_promotion(self):
        """It should deserialize a dictionary into a Promotion"""
        data = {
            "name": "Back to School",
            "promo_type": "AMOUNT_OFF",
            "product_id": 1005,
            "amount": 7.0,
            "start_date": "2025-08-01",
            "end_date": "2025-08-15",
            "status": False,
        }
        promo = Promotion()
        promo.deserialize(data)
        self.assertEqual(promo.name, "Back to School")
        self.assertEqual(promo.promo_type, "AMOUNT_OFF")
        self.assertFalse(promo.status)

    def test_find_by_name(self):
        """It should find promotions by name"""
        promo = Promotion(
            name="Mega Discount",
            promo_type=PromoType.AMOUNT_OFF.name,
            product_id=1006,
            amount=12.0,
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 30),
            status=True,
        )
        promo.create()
        results = Promotion.find_by_name("Mega Discount")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].product_id, 1006)
        self.assertTrue(results[0].status)

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

    def _make_promo(self, name="Failure Path"):
        return Promotion(
            name=name,
            promo_type=PromoType.BOGO.name,
            product_id=222,
            amount=1.0,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 2),
            status=True,
        )

    # -----------------------------------------------------------------
    #  __repr__
    # -----------------------------------------------------------------
    def test_repr(self):
        """__repr__ should include name and id in the expected format"""
        promo = self._make_promo("Repr Test")
        promo.id = 42  # fake primary key to avoid DB hit
        self.assertEqual(repr(promo), "<Promotion Repr Test id=[42]>")

    # -----------------------------------------------------------------
    #  Error handling in create / update / delete
    # -----------------------------------------------------------------
    def test_create_database_error(self):
        """create() must rollback and raise DataValidationError on commit failure"""
        promo = self._make_promo()
        with patch.object(
            db.session, "commit", side_effect=Exception("boom")
        ), patch.object(db.session, "rollback") as mocked_rb:
            with self.assertRaises(DataValidationError):
                promo.create()
            mocked_rb.assert_called_once()

    def test_update_database_error(self):
        """update() must rollback and raise DataValidationError on commit failure"""
        promo = self._make_promo()
        promo.create()  # normal path first
        promo.amount = 99.0
        with patch.object(
            db.session, "commit", side_effect=Exception("boom")
        ), patch.object(db.session, "rollback") as mocked_rb:
            with self.assertRaises(DataValidationError):
                promo.update()
            mocked_rb.assert_called_once()

    def test_delete_database_error(self):
        """delete() must rollback and raise DataValidationError on commit failure"""
        promo = self._make_promo()
        promo.create()
        with patch.object(
            db.session, "commit", side_effect=Exception("boom")
        ), patch.object(db.session, "rollback") as mocked_rb:
            with self.assertRaises(DataValidationError):
                promo.delete()
            mocked_rb.assert_called_once()

    # -----------------------------------------------------------------
    #  deserialize() – error branches
    # -----------------------------------------------------------------
    def test_deserialize_missing_key(self):
        """Missing required field should raise the KeyError-wrapped variant"""
        bad = {
            "promo_type": "PERCENT_OFF",
            "product_id": 123,
            "amount": 5,
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "status": True,
        }
        with self.assertRaises(DataValidationError) as ctx:
            Promotion().deserialize(bad)
        self.assertIn("missing name", str(ctx.exception))

    def test_deserialize_bad_or_malformed_data(self):
        """Wrong field types / bad ISO date ⇒ ValueError/TypeError branch"""
        bad = {
            "name": "Bad Data",
            "promo_type": "PERCENT_OFF",
            "product_id": "not-int",
            "amount": "not-float",
            "start_date": "not-a-date",
            "end_date": "also-bad",
            "status": "not-a-bool",
        }
        with self.assertRaises(DataValidationError) as ctx:
            Promotion().deserialize(bad)
        self.assertIn("bad or malformed data", str(ctx.exception))

    def test_deserialize_attribute_error(self):
        """Force an AttributeError while inside the try-block so the “Invalid attribute” branch executes."""
        good = {
            "name": "Attr Error",
            "promo_type": "PERCENT_OFF",
            "product_id": 999,
            "amount": 10,
            "start_date": "2025-03-01",
            "end_date": "2025-03-31",
            "status": True,
        }
        promo = Promotion()

        original_setattr = Promotion.__setattr__

        def broken_setattr(self, key, value):
            if key == "name":
                raise AttributeError("name")
            return original_setattr(self, key, value)

        try:
            Promotion.__setattr__ = broken_setattr
            with self.assertRaises(DataValidationError) as ctx:
                promo.deserialize(good)
            self.assertIn("Invalid attribute", str(ctx.exception))
        finally:
            Promotion.__setattr__ = original_setattr
