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
    buildings: collection = db.Buildings

    buildings.delete_many({})
    buildings.create_index([("building_name", pymongo.ASCENDING)], unique=True)
    buildings.insert_many([
        {"building_name": "VEC"},
        {"building_name": "ECS"},
        {"building_name": "HC"},
        {"building_name": "HS"},
        {"building_name": "LH"},
        {"building_name": "FA1"},
        {"building_name": "SSSC"},
        {"building_name": "BMAC"}
    ])

    return buildings

def createRooms():
    rooms: collection = db.Rooms

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
    db.command('collMod', 'Rooms', **room_validator)

    rooms.delete_many({})
    rooms.create_index([("building_name", pymongo.ASCENDING), ("room_number", pymongo.ASCENDING)], unique=True)
    buildingNames = []
    buildings = db.Buildings
    for line in buildings.find():
        buildingNames.append(line["building_name"])

    for bn in buildingNames:
        randoms = random.sample(range(100, 460), 3)
        rooms.insert_many([
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[0])},
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[1])},
            {"building_name": DBRef("Buildings", bn), "room_number" : int(randoms[2])}
        ])

    return rooms

def createTables():
    buildings = createBuildings()
    rooms = createRooms()

    return buildings, rooms


if __name__ == "__main__":
    db = setup()
    print('In main: ', db.list_collection_names())

    buildings, rooms = createTables()

    printTable(rooms)
