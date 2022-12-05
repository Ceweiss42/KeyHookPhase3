import getpass
import pymongo
from pymongo import MongoClient


class Utilities:


    """Return the size document for the given name."""
    @staticmethod
    def get_doorname(db, door_name):
        result = db.DoorNames.find_one({"door_name": door_name})['door_name']
        return result
    """Return the room document for the given name."""
    @staticmethod
    def get_room(db, room):
        result = db.Rooms.find_one({"room_number": room})['room_number']
        return result

    """Return the building document for the given name."""
    @staticmethod
    def get_building(db, building):
        result = db.Buildings.find_one({"building_name": building})['building_name']
        return result
    """Return the hook document for the given name."""
    @staticmethod
    def get_hook(db, hook):
        result = db.Hooks.find_one({"hook_number": hook})['hook_number']
        return result
    """Return the key document for the given name."""
    @staticmethod
    def get_key(db, key):
        result = db.Keys.find_one({"key_number": key})['key_number']
        return result

