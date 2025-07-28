"""
Models for YourResourceModel

All of the models are stored in this module
"""

import logging
from enum import Enum
from datetime import date
from flask_sqlalchemy import SQLAlchemy


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PromoType(Enum):
    """Enumeration of valid Promotion Types"""

    PERCENT_OFF = "PERCENT_OFF"
    BOGO = "BOGO"
    AMOUNT_OFF = "AMOUNT_OFF"


class Promotion(db.Model):  # pylint: disable=too-many-instance-attributes
    """Class that represents a Promotion"""

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    promo_type = db.Column(db.String(20), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)

    # probably need to add how much off, etc field here or incorporate it into promo_type

    def __repr__(self):
        return f"<Promotion {self.name} id=[{self.id}]>"

    def create(self):
        """Creates a Promotion in the database"""
        logger.info("Creating %s", self.name)
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating Promotion: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates a Promotion in the database"""
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating Promotion: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Promotion from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting Promotion: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "promo_type": self.promo_type,
            "product_id": self.product_id,
            "amount": self.amount,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            promo_type = data["promo_type"]
            if promo_type not in PromoType.__members__:
                raise DataValidationError(f"Invalid promo_type: {promo_type}")
            self.promo_type = promo_type
            self.product_id = int(data["product_id"])
            self.amount = float(data["amount"])
            self.start_date = date.fromisoformat(data["start_date"])
            self.end_date = date.fromisoformat(data["end_date"])
            self.status = bool(data.get("status", True))
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Promotion: missing " + error.args[0]
            ) from error
        except (TypeError, ValueError) as error:
            raise DataValidationError(
                "Invalid Promotion: bad or malformed data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all Promotions in the database"""
        logger.info("Processing all Promotions")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Promotion by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Promotions with the given name

        Args:
            name (string): the name of the Promotions to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_by_type(cls, promo_type):
        """Returns all promotions that match the given type"""
        return cls.query.filter_by(promo_type=promo_type).all()
