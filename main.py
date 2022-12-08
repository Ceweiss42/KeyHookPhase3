from pymongo import MongoClient
from pymongo import collection
import pymongo
from bson.dbref import DBRef
import random
from Utilities import Utilities
import time
import datetime


def setup():
    client = MongoClient("mongodb+srv://group8:group8@keyhookphase3.hfewn3v.mongodb.net/?retryWrites=true&w=majority")
    mdb = client.KeyHookPhase3
    return mdb


def printCollectionLine(collectionLine):
    output = ""
    for k in collectionLine.keys():
        if k == "_id":
            continue

        else:
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
    e.create_index([("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING),
                    ("employee_id", pymongo.ASCENDING)], unique=True)
    insert_students = e.insert_many([
        {"last_name": "Aguilar", "first_name": "Ed", "employee_id": 1},
        {"last_name": "Weiss", "first_name": "Cam", "employee_id": 2},
        {"last_name": "Ha", "first_name": "Jimmy", "employee_id": 3},
        {"last_name": "Lucena", "first_name": "Jeff", "employee_id": 4},
        {"last_name": "Brown", "first_name": "Dave", "employee_id": 5}
    ])

    return e


def createDoorNames():
    # create the doornames collection and populate it  with data
    db.DoorNames.drop()
    dn: collection = db.DoorNames
    dn.create_index([("door_name", pymongo.ASCENDING)], unique=True)
    insert_doornames = dn.insert_many([
        {"door_name": "West"},
        {"door_name": "East"},
        {"door_name": "North"},
        {"door_name": "South"},
        {"door_name": "Front"},
        {"door_name": "Back"},
    ])

    return dn


def createHooks():
    db.Hooks.drop()
    h: collection = db.Hooks
    h.create_index([("hook_number", pymongo.ASCENDING)], unique=True)

    insert_hooks = h.insert_many([
        {"hook_number": 1},
        {"hook_number": 2},
        {"hook_number": 3},
        {"hook_number": 4},
        {"hook_number": 5},
        {"hook_number": 6},
        {"hook_number": 7},
        {"hook_number": 8},
    ])

    return h

def createRequests():
    db.Requests.drop()
    req: collection = db.Requests

    req.create_index([("request_id", pymongo.ASCENDING)], unique=True)
    req.create_index([("room_number", pymongo.ASCENDING), ("building_name", pymongo.ASCENDING),
                      ("employee_id", pymongo.ASCENDING), ("requested_date", pymongo.ASCENDING),
                      ("key_number", pymongo.ASCENDING), ("loaned_date", pymongo.ASCENDING)], unique=False)

    for i in range(10):
        wantedDoor = Utilities.getDoors(db)
        inserted_requests = req.insert_many([
            {
                "request_id": Utilities.getNextRequestID(db),
                "room_number": DBRef("Rooms", randomRoom[0]),
                "building_name": DBRef("Rooms", randomRoom[1]),
                "employee_id": DBRef("Employees", Utilities.getRandomEmployeeID(db)),
                "requested_date": datetime.datetime.now(),
                "key_number": DBRef("Keys", "_______"),
                "loaned_date": None
            }
        ])

    return req


def createDoors():
    db.Doors.drop()
    d: collection = db.Doors
    d.create_index([("door_name", pymongo.ASCENDING), ("room_number", pymongo.ASCENDING),
                        ("building_name", pymongo.ASCENDING)], unique=True)

    dns = Utilities.get_doorname(db)
    roomTuples = Utilities.get_room(db)
    for r in roomTuples:
        randoms = random.sample(range(0, len(dns)), 2)

        for i in range(2):
            insert_doors = d.insert_many([
                {"door_name": DBRef("Doornames", dns[randoms[i]]),
                 "room_number": DBRef("Rooms", r[0]),
                 "building_name": r[1]}
            ])

    return d

def createHookDoors():
    '''
    door_name = Column('door_name', String(20), ForeignKey('doors.door_name'), nullable=False, primary_key=True)
    room_number = Column('room_number', Integer, ForeignKey('rooms.room_number'), nullable=False, primary_key=True)
    building_name = Column('building_name', String(40), ForeignKey('doors.building_name'), nullable=False,
                           primary_key=True)
    hook_number = Column('hook_number', Integer, ForeignKey('hooks.hook_number'), nullable=False, primary_key=True)
    '''
    db.HookDoors.drop()
    hd: collection = db.HookDoors
    hd.create_index([("door_name", pymongo.ASCENDING), ("room_number", pymongo.ASCENDING),
                     ("building_name", pymongo.ASCENDING), ("hook_number", pymongo.ASCENDING)], unique=True)

    everyDoor = Utilities.getDoors(db)
    for door in everyDoor:
        inserted_HookDoors = hd.insert_many([
            {
                "door_name":  door[2],
                "room_number": door[0],
                "building_name": door[1],
                "hook_number": DBRef("Hooks", Utilities.getRandomHook(db))
            }
        ])

    return hd



def createKeys():
    db.Keys.drop()
    k: collection = db.Keys
    k.create_index([("key_number", pymongo.ASCENDING)])

    insert_keys = k.insert_many([
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

    return k


def createTables():
    buildings = createBuildings()
    rooms = createRooms()
    employees = createEmployees()
    doornames = createDoorNames()
    hooks = createHooks()
    doors = createDoors()
    keys = createKeys()
    hookdoors = createHookDoors()


    return buildings, rooms, employees, doornames, doors, hooks, keys, hookdoors


def printOptions():
    print("0. Exit")
    print("1. Print Table(s)")
    print("2. Something Else")


def runPrintOptions():
    printTable(hookdoors)


def menu():
    print("------------------------------")
    choice = -9
    while choice != 0:
        try:
            printOptions()
            choice = int(input("What would you like to do? "))
            match choice:
                case 0:
                    break
                case 1:
                    runPrintOptions()
                    continue
                case _:
                    print("Input not recognized")
                    menu()
                    break

        except all:
            print("Input not recognized")
            menu()


if __name__ == "__main__":
    db = setup()

    buildings, rooms, employees, doornames, doors, hooks, keys, hookdoors = createTables()
    menu()

    print("Closing the program...")
    time.sleep(2)
    exit()
