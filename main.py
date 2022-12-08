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
        if type(collectionLine[k]) == DBRef:
            output += str(k) + ": " + str(collectionLine[k].id) + "    "
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
                      ("key_number", pymongo.ASCENDING), ("loaned_date", pymongo.ASCENDING),
                      ("door_name", pymongo.ASCENDING)], unique=False)
    allDoors = Utilities.getDoors(db)
    random.shuffle(allDoors)
    for _ in range(20):
        door = allDoors.pop()
        inserted_requests = req.insert_many([
            {
                "request_id": Utilities.getNextRequestID(db),
                "room_number": door[0],
                "building_name": door[1],
                "employee_id": DBRef("Employees", Utilities.getRandomEmployeeID(db)),
                "requested_date": datetime.datetime.now(),
                "key_number": Utilities.getFirstKeyByDoor(db, door),
                "loaned_date": None,
                "door_name": door[2]
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
                {"door_name": DBRef("DoorNames", dns[randoms[i]]),
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

def updateRequestLoanDate(r):
    db.Requests.replace_one({'_id': r['_id']},
                            {
                                "request_id": r["request_id"],
                                "room_number": r['room_number'],
                                "building_name": r['building_name'],
                                "employee_id": r['employee_id'],
                                "requested_date": r['requested_date'],
                                "key_number": r['key_number'],
                                "loaned_date": datetime.datetime.now(),
                                "door_name": r['door_name']
                            })

def createLossKeys():
    db.LossKeys.drop()
    lk: collection = db.LossKeys
    lk.create_index([("request_id", pymongo.ASCENDING)], unique=True)
    lk.create_index([("loss_date", pymongo.ASCENDING)], unique=False)

    length = 0

    reqsList = []

    for x in db.Requests.find():
        length += 1
        reqsList.append(x)

    randoms = random.sample(range(0, length), 5)

    for r in reqsList:
        if r['request_id'] in randoms:
            updateRequestLoanDate(r)

    for i in randoms:
        inserted_LKs = lk.insert_many([
            {
                "request_id": DBRef("Requests", reqsList[i]['request_id']),
                "loss_date": datetime.datetime.now()
            }
        ])

    return lk

def createReturnKeys():
    db.ReturnKeys.drop()
    rk: collection = db.ReturnKeys
    rk.create_index([("request_id", pymongo.ASCENDING)], unique=True)
    rk.create_index([("return_date", pymongo.ASCENDING)], unique=False)

    length = 0

    reqsList = []

    for x in db.Requests.find({'loaned_date': None}):
        length += 1
        reqsList.append(x)

    randoms = random.sample(range(0, length), 5)

    for r in reqsList:
        if r['request_id'] in randoms:
            updateRequestLoanDate(r)

    for i in randoms:
        inserted_RKs = rk.insert_many([
            {
                "request_id": DBRef("Requests", reqsList[i]['request_id']),
                "return_date": datetime.datetime.now()
            }
        ])

    return rk

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
    requests = createRequests()
    losskeys = createLossKeys()
    returnkeys = createReturnKeys()


    return buildings, rooms, employees, doornames, doors, hooks, keys, hookdoors, requests, losskeys, returnkeys

def createNewKeySequence():
    print("All Hooks:")
    printTable(db.Hooks)
    print("Please enter a Hook Number to create a new Key For:")
    try:
        choice = int(input())
        hook = db.Hooks.find_one({"hook_number": choice})
        if hook:
            db.Keys.insert_many([{
                "key_number": DBRef("hooks", choice)
            }])
            print("Successfully created a new Key!")
            print("New Keys Table:")
            printTable(keys)
        else:
            print("No hook found for hook number", str(choice))

    except Exception as e:
        print("Could not understand user input. Returning to main Menu\n\n")

def getAllRoomsIHaveAccessTo(id):
    me = db.Employees.find_one({"employee_id": id})
    if not me:
        print("No user found")
        return

    correctRequests = []
    allMyRequests = db.Requests.find()
    for req in allMyRequests:
        if int(req["employee_id"].id) == id and req["loaned_date"] is not None:
            correctRequests.append(req)

    #here
    lks = db.LossKeys.find()
    rks = db.ReturnKeys.find()
    for r in correctRequests:
        for lk in lks:
            if r["request_id"] == int(lk["request_id"].id):
                correctRequests.remove(r)
                break

        for rk in rks:
            if r["request_id"] == int(rk["request_id"].id):
                correctRequests.remove(r)
                break

    #now we have all requests that we currently have a key for
    hooksList = []
    for x in correctRequests:
        hook = db.Hooks.find_one({"hook_number": int(x["key_number"].id)})
        if hook not in hooksList:
            hooksList.append(hook)

    access = []

    hds = db.HookDoors.find()
    for hd in hds:
        ac = False
        for h in hooksList:
            if hd["hook_number"].id == h["hook_number"]:
                ac = True

        if not ac:
            room = db.Rooms.find_one({"building_name": hd["building_name"].id,
                                      "room_number": hd["room_number"].id})
            if room not in access:
                access.append(room)

    #here

    return access


def requestAccessToRoom():
    try:
        user_id = int(input("Please enter your ID\n"))
        emp = db.Employees.find_one({"employee_id": user_id})
        if emp:
            count = 0
            roomsList = []
            allRooms = db.Rooms.find()
            for r in allRooms:
                print(str(count), ". ", end="")
                printCollectionLine(r)
                roomsList.append(r)
                count += 1


            chosenRoom = roomsList[int(input("Please enter the index of the wanted room: "))]
            if chosenRoom:
                if chosenRoom in getAllRoomsIHaveAccessTo(user_id):
                    print("You already have access to this room!")

                else:
                    doorsInBuilding = db.Doors.find({"building_name": chosenRoom["building_name"]})
                    door = None
                    for d in doorsInBuilding:
                        if int(d["room_number"].id) == chosenRoom["room_number"]:
                            door = d
                            break

                    key_number = db.HookDoors.find_one({"building_name": door["building_name"],
                                                        "room_number": door["room_number"],
                                                        "door_name": door["door_name"]})["hook_number"]

                    print(door)
                    db.Requests.insert_many([
                        {
                            "request_id": Utilities.getNextRequestID(db),
                            "room_number": DBRef("Room", chosenRoom["room_number"]),
                            "building_name": chosenRoom["building_name"],
                            "employee_id": DBRef("Employees", user_id),
                            "requested_date": datetime.datetime.now(),
                            "key_number": key_number,
                            "loaned_date": None,
                            "door_name": door["door_name"]
                        }
                    ])

                    print("Successfully submitted a request!")


            else:
                print("There is no room at the given index! Returning to main menu.")

        else:
            print("No employee found with ID", user_id)

    except ValueError as e:
        print("EXCEPTION", e)
        print("Could not understand user input. Returning to main Menu\n\n")

def printOptions():
    print("0. Exit")
    print("1. Print Table(s)")
    print("2. Create a new Key")
    print("3. Request Access to a room")
    print("4. Issue a key (Update Key Request)")
    print("5. ")


def runPrintTable():

    for i in range(len(tableList)):
        print(str(i) + ". " + str(tableList[i].name))

    try:
        choice = int(input("What table would you like to print?"))
        printTable(tableList[choice])
        print("\n\n")

    except Exception as e:
        print("Could not understand input. please try again")
        runPrintTable()


def menu():

    choice = -9
    while choice != 0:
        try:
            print("------------------------------")
            printOptions()
            choice = int(input("What would you like to do? "))
            if choice == 0:
                return None

            elif choice == 1:
                runPrintTable()

            elif choice == 2:
                createNewKeySequence()
            elif choice == 3:
                requestAccessToRoom()
            else:
                print("Input not on the list")

        except ValueError as e:
            print(e)
            print("Input not recognized")


if __name__ == "__main__":
    db = setup()

    buildings, rooms, employees, doornames, doors, hooks, keys, hookdoors, requests, losskeys, returnkeys = createTables()

    tableList = [buildings, rooms, employees, doornames, doors, hooks, keys, hookdoors, requests, losskeys, returnkeys]
    menu()

    print("Closing the program...")
    time.sleep(2)
    exit()
