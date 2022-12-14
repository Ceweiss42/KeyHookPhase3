import getpass
import pymongo
from pymongo import MongoClient
import random


class Utilities:


    """Get a random room"""
    @staticmethod
    def getRandomRoom(db):
        list = Utilities.get_room(db)
        return list[random.randint(0, len(list))]


    @staticmethod
    def getFirstKeyByDoor(db, door):

        allHD = db.HookDoors.find()
        for hd in allHD:
            if (hd['building_name'].id == door[1].id
                and hd['room_number'].id == door[0].id
                and hd['door_name'].id == door[2].id):
                return hd['hook_number']
        return None

    @staticmethod
    def getRandomHook(db):
        out = []
        hooks = db.Hooks.find()
        for h in hooks:
            out.append(h["hook_number"])
        return out[random.randint(0, len(out) - 1)]

    @staticmethod
    def getDoors(db):
        out = []
        doors = db.Doors.find()
        for d in doors:
            out.append([d["room_number"], d["building_name"], d["door_name"]])
        return out

    @staticmethod
    def getRandomEmployeeID(db):
        employees = db.Employees.find()

        ids = []
        for e in employees:
            id = int(e["employee_id"])
            ids.append((id))

        r = random.randint(0, len(ids) - 1)
        return ids[r]
    """Get the next available request id """
    @staticmethod
    def getNextRequestID(db):
        out = 0
        res = db.Requests.find()
        for _ in res:
            out += 1

        return out
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

