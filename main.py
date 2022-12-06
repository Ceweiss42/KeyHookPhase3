from pymongo import MongoClient
from pymongo import collection
import pymongo
from bson.dbref import DBRef
import random

def setup():
    client = MongoClient("mongodb+srv://group8:group8@keyhookphase3.hfewn3v.mongodb.net/?retryWrites=true&w=majority")
    db = client.KeyHookPhase3
    return db

def printCollectionLine(collectionLine):
    output = ""
    for k in collectionLine.keys():
        if k == "_id":
            continue
        output += str(k) + ": " + str(collectionLine[k]) + "    "
    print(output)

def printTable(table : collection):
    lines = table.find()
    for line in lines:
        printCollectionLine(line)

def createBuildings():
    db.Buildings.drop()
    b: collection = db.Buildings

    b.create_index([("building_name", pymongo.ASCENDING)], unique=True)
    b.insert_many([
        {"building_name": "VEC"},
        {"building_name": "ECS"},
        {"building_name": "HC"},
        {"building_name": "HS"},
        {"building_name": "LH"},
        {"building_name": "FA1"},
        {"building_name": "SSSC"},
        {"building_name": "BMAC"}
    ])

    return b

def createRooms():
    db.Rooms.drop()
    r: collection = db.Rooms

    room_validator = {
        'validator': {
            '$jsonSchema': {
                # Signifies that this schema is complex, has parameters within it.
                # These can be nested.
                'bsonType': "object",
                'description': "A room within a building",
                'required': ["building_name", "room_number"],
                'additionalProperties': False,
                'properties': {
                    # I would LIKE to demand an ObjectID here, but I cannot figure out how
                    '_id': {},
                    'building_name': {
                        'bsonType': "DBRef",
                        "description": "name of building room is in"
                    },
                    'room_number': {
                        # the type "number" matches integer, decimal, double, and long
                        'bsonType': "number",
                        "description": "number of the room",
                    }
                }
            }
        }
    }
#    db.command('collMod', 'Rooms', **room_validator)

    rooms.create_index([("building_name", pymongo.ASCENDING), ("room_number", pymongo.ASCENDING)], unique=True)
    buildingNames = []
    b = db.Buildings
    for line in b.find():
        buildingNames.append(line["building_name"])

    for bn in buildingNames:
        randoms = random.sample(range(100, 460), 3)
        r.insert_many([
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[0])},
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[1])},
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[2])}
        ])

    return r

def createEmployees():
    db.Employees.drop()
    e: collection = db.Employees
    e.create_index([("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)], unique=True)
    insert_students = e.insert_many([
        {"last_name": "Aguilar", "first_name": "Ed"},
        {"last_name": "Weiss", "first_name": "Cam"},
        {"last_name": "Ha", "first_name": "Jimmy"},
        {"last_name": "Lucena", "first_name": "Jeff"},
        {"last_name": "Brown", "first_name": "Dave"},
    ])

    return e

def createDoorNames():

    return dn

def createTables():
    buildings = createBuildings()
    rooms = createRooms()
    employees = createEmployees()
    doornames = createDoorNames()

    return buildings, rooms, employees, doornames

    db.DoorNames.drop()
    db.Hooks.drop()
    db.Doors.drop()
    db.Keys.drop()


    #create the doornames collection and populate it  with data
    doornames = db.DoorNames
    doornames.create_index([("door_name", pymongo.ASCENDING)],  unique=True)
    insert_doornames = doornames.insert_many([
        {"door_name": "West"},
        {"door_name": "East"},
        {"door_name": "North"},
        {"door_name": "South"},
        {"door_name": "Front"},
        {"door_name": "Back"},
        ])

    #create the hooks collection and populate it  with data
    hooks = db.Hooks
    hooks.create_index([("hook_number", pymongo.ASCENDING)], unique=True)
    insert_hooks = hooks.insert_many([
        {"hook_number": 1},
        {"hook_number": 2},
        {"hook_number": 3},
        {"hook_number": 4},
        {"hook_number": 5},
        {"hook_number": 6},
        {"hook_number": 7},
        {"hook_number": 8},
        ])

    # create the doors collection and populate it  with data
    doors = db.Doors
    doors.create_index([("doorname", pymongo.ASCENDING),("room_number", pymongo.ASCENDING),
                        ("building_name",pymongo.ASCENDING)], unique=True)
    insert_doors = doors.insert_many([
        {"door_name": DBRef("doornames", Utilities.get_doorname(db,'West')),
         "room_number": DBRef("rooms", Utilities.get_room(db,403)),
         "building_name": DBRef("buildings", Utilities.get_building(db,'VEC'))},
        {"door_name": DBRef("doornames", Utilities.get_doorname(db, 'East')),
         "room_number": DBRef("rooms", Utilities.get_room(db, 297)),
         "building_name": DBRef("buildings", Utilities.get_building(db, 'VEC'))},
        {"door_name": DBRef("doornames", Utilities.get_doorname(db, 'Front')),
         "room_number": DBRef("rooms", Utilities.get_room(db, 180)),
         "building_name": DBRef("buildings", Utilities.get_building(db, 'VEC'))},
        {"door_name": DBRef("doornames", Utilities.get_doorname(db, 'Front')),
         "room_number": DBRef("rooms", Utilities.get_room(db, 397)),
         "building_name": DBRef("buildings", Utilities.get_building(db, 'ECS'))},
        {"door_name": DBRef("doornames", Utilities.get_doorname(db, 'South')),
         "room_number": DBRef("rooms", Utilities.get_room(db, 127)),
         "building_name": DBRef("buildings", Utilities.get_building(db, 'ECS'))},
        {"door_name": DBRef("doornames", Utilities.get_doorname(db, 'East')),
         "room_number": DBRef("rooms", Utilities.get_room(db, 417)),
         "building_name": DBRef("buildings", Utilities.get_building(db, 'ECS'))}
        ])

    # create the keys collection and populate it  with data
    keys = db.Keys
   # keys.create_index([("_id", pymongo.ASCENDING)], unique=True) --Constraint not needed because multiple keys can have the same hook
    insert_keys = keys.insert_many([
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 1))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 2))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 3))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 4))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 5))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 6))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 7))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 8))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 1))},
        {"key_number": DBRef("hooks", Utilities.get_hook(db, 2))},
        ])

if __name__ == "__main__":
    db = setup()
    print('In main: ', db.list_collection_names())

    buildings, rooms, employees, doornames = createTables()

    printTable(rooms)
