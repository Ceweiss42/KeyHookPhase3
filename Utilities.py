import getpass
import pymongo
from pymongo import MongoClient


class Utilities:


    """Return the size document for the given name."""
    @staticmethod
    def get_doorname(db):
        output = []
        result = db.DoorNames.find()
        for line in result:
            output.append(line['door_name'])
        return output
    """Return the room document for the given name."""
    @staticmethod
    def get_room(db):
        output = []
        result = db.Rooms.find()
        for r in result:
            output.append((r['room_number'], r['building_name']))
        return output

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

