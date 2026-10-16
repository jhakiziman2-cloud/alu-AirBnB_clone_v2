#!/usr/bin/python3
"""Defines the Place class and the place_amenity association table."""
from os import getenv
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
import models
from models.base_model import BaseModel, Base

place_amenity = Table(
    "place_amenity", Base.metadata,
    Column("place_id", String(60), ForeignKey("places.id"),
           primary_key=True, nullable=False),
    Column("amenity_id", String(60), ForeignKey("amenities.id"),
           primary_key=True, nullable=False))


class Place(BaseModel, Base):
    """Represents a place to rent (table places)."""
    __tablename__ = "places"
    city_id = Column(String(60), ForeignKey("cities.id"), nullable=False)
    user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=True)
    number_rooms = Column(Integer, nullable=False, default=0)
    number_bathrooms = Column(Integer, nullable=False, default=0)
    max_guest = Column(Integer, nullable=False, default=0)
    price_by_night = Column(Integer, nullable=False, default=0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    if getenv("HBNB_TYPE_STORAGE") == "db":
        reviews = relationship("Review", backref="place",
                               cascade="all, delete")
        amenities = relationship("Amenity", secondary=place_amenity,
                                 back_populates="place_amenities",
                                 viewonly=False)
    else:
        amenity_ids = []

        @property
        def reviews(self):
            """Return the list of Review instances linked to this Place."""
            from models.review import Review
            return [review for review in models.storage.all(Review).values()
                    if review.place_id == self.id]

        @property
        def amenities(self):
            """Return the list of Amenity instances linked to this Place.

            Calling append() on the returned list links the Amenity.
            """
            from models.amenity import Amenity
            everything = models.storage.all(Amenity).values()
            found = [amenity for amenity in everything
                     if amenity.id in self.amenity_ids]
            return _AmenityList(self, found)

        @amenities.setter
        def amenities(self, obj):
            """Link an Amenity to this Place (other types are ignored)."""
            from models.amenity import Amenity
            if isinstance(obj, Amenity) and obj.id not in self.amenity_ids:
                self.amenity_ids = self.amenity_ids + [obj.id]


class _AmenityList(list):
    """List of Amenity objects whose append() links the Amenity to a Place."""

    def __init__(self, place, items):
        """Initialize the list with its owner Place and its items."""
        super().__init__(items)
        self._place = place

    def append(self, obj):
        """Link obj to the Place if it is an Amenity, then store it."""
        before = len(self._place.amenity_ids)
        self._place.amenities = obj
        if len(self._place.amenity_ids) > before:
            super().append(obj)
