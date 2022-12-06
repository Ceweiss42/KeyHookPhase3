from pymongo import MongoClient
from pymongo import collection
import pymongo
from bson.dbref import DBRef
import random
from Utilities import Utilities

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

    r.create_index([("building_name", pymongo.ASCENDING), ("room_number", pymongo.ASCENDING)], unique=True)
    buildingNames = []
    b = db.Buildings
    for line in b.find():
        buildingNames.append(line["building_name"])

    for bn in buildingNames:
        randoms = random.sample(range(100, 460), 2)
        r.insert_many([
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[0])},
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[1])},
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
    hooks = createHooks()
    doors = createDoors()
    keys = createKeys()


    return buildings, rooms, employees, doornames, doors, hooks, keys



if __name__ == "__main__":
    db = setup()
    print('In main: ', db.list_collection_names())

    buildings, rooms, employees, doornames = createTables()

    printTable(doors)
