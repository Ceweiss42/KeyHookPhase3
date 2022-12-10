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

def issueKey():
    print("Welcome to the issuing portal. First, select an employee")
    emps = db.Employees.find()
    for e in emps:
        print(printCollectionLine(e))
    try:
        choice = int(input("Please enter the employee ID: "))
        chosenEmployee = db.Employees.find_one({"employee_id": choice})

        if not chosenEmployee:
            print("Uh oh, something broke! No employee given from DB")
            return

        myReqs = []
        notGiven = db.Requests.find({"loaned_date": None})
        for r in notGiven:
            if r['employee_id'].id == chosenEmployee["employee_id"]:
                myReqs.append(r)

        for r in myReqs:
            printCollectionLine(r)

        req = db.Requests.find_one({"request_id": int(input("please enter request id: "))})
        if not req:
            print("no recognized request given")
            return

        updateRequestLoanDate(req)


    except Exception as e:
        print("Something went wrong!")
        return
    '''try:
        user_id = int(input("Please enter your ID\n"))
        emp = db.Employees.find_one({"employee_id": user_id})
        if emp:
            print("do the code")
            #1.take the employee id and print out all of their requests
            #2.ask them which key do you want to issue
            #3.update the loaned out date
            #4.print it out and say that the key was issued successfully

            #this prints out all of the requests for the employee
            requestList = []
            allRequest = db.Requests.find()
            for x in allRequest:
                emp_request = db.Requests.find({"employee_id": int(x["employee_id"].id)})
                if emp_request not in requestList:
                    requestList.append(emp_request) #created a list that holds all of the requests made by the emp
                print(emp_request) #having trouble printing it out

            chosenRequest = requestList[int(input("Please enter which key you want to issue : "))]

            if chosenRequest:
                if chosenRequest in requestList:
                    print("You already have access to this key! ")
                #continue on from here
            else:
                print("Sorry there is no key of that number which can be issued out. ")




        else:
            print("Sorry there is no employee with that idea.")
    except ValueError as e:
        print("Exception", e)
        print("The input you tried giving is of the wrong type. Please try again\n\n")'''

def reportLossKey():
    try:
        user_id = int(input("Please enter your ID\n"))
        emp = db.Employees.find_one({"employee_id": user_id})
        if emp:
            myReqsList = []
            allReqs = db.Requests.find()
            for r in allReqs:
                if int(r["employee_id"].id) == user_id and r["loaned_date"]:
                    myReqsList.append(r)

            for r in myReqsList:
                returns = db.ReturnKeys.find()
                for ret in returns:
                    if int(ret["request_id"].id) == r["request_id"]:
                        # we have returned this one
                        myReqsList.remove(r)

                losses = db.LossKeys.find()
                for l in losses:
                    if int(l["request_id"].id) == r["request_id"]:
                        # we have returned this one
                        myReqsList.remove(r)

            # now myReqsList contains only the ones that we currently have
            for r in myReqsList:
                printCollectionLine(r)

            if len(myReqsList) > 0:

                lossKey = int(input("Which of these keys was lost\n"))
                db.LossKeys.insert_one({"request_id": DBRef("Requests", lossKey), "loss_date": datetime.datetime.now()})
                print("The key has been reported lost")
            else:
                print("You cannot report a loss key since you have none!")
        else:
            print("Sorry you don't exist :( ")
    except ValueError as e:
        print("Exception", e)
        print("The input you tried giving is of the wrong type. Please try again\n\n")


def addNewDoor():
    roomsList = []
    count = 0
    for r in db.Rooms.find():
        roomsList.append(r)
        print(str(count), "  ", end = "")
        printCollectionLine(r)
        count += 1

    allDoorNames = []
    for dn in db.DoorNames.find():
        allDoorNames.append(dn["door_name"])


    try:
        roomChoice = roomsList[int(input("please enter the index of wanted room"))]

        roomDoors = db.Doors.find({"building_name": roomChoice["building_name"]})
        for rd in roomDoors:
            if int(rd["room_number"].id) == roomChoice["room_number"]:
                allDoorNames.remove(rd["door_name"].id)

        db.Doors.insert_one({
            "door_name": DBRef("DoorNames", allDoorNames[0]),
            "room_number": DBRef("Rooms", roomChoice["room_number"]),
            "building_name": roomChoice["building_name"]

        })

        print("Door added")
    except Exception as e:
        print("Cannot add a new door, all door names taken!")

# def addNewDoor():
#     buildingsList = []
#     allBuildings = db.Buildings.find()
#     count = 0
#     for r in allBuildings:
#         print(str(count), ". ", end="")
#         printCollectionLine(r)
#         buildingsList.append(r)
#         count += 1
#
#     req_Building = buildingsList[int(input("Please select the building you would like to add a new door too: "))]
#     # db.Keys.delete_one({"_id": chosenkey["_id"]})
#     # print("The key has been deleted")
#     db.



def printOptions():
    print("0. Exit")                                             #
    print("1. Print Table(s)")                                   #
    print("2. Create a new Key")                                 #
    print("3. Request Access to a room")                         #
    print("4. Issue a key (Update Key Request)")                 #
    print("5. Report lost key")                                  #
    print("6. Rooms that an employee can enter")
    print("7. Delete a key")                                     #
    print("8. Delete an employee")                               #
    print("9. Add a new door")
    print("10. Update access request to move it to a new employee")
    print("11. Employees who can enter a room")                  #


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

def deleteKey():
    keysList = []
    allKeys = db.Keys.find()
    count = 0
    for r in allKeys:
        print(str(count), ". ", end="")
        printCollectionLine(r)
        keysList.append(r)
        count += 1
    #add try and catch that checks if the key is owned by anyone
    chosenkey = keysList[int(input("Please enter the index of the key you want to delete: "))]
    db.Keys.delete_one({"_id": chosenkey["_id"]})
    print("The key has been deleted")

    keysList = []
    allKeys = db.Keys.find()
    count = 0
    for r in allKeys:
        print(str(count), ". ", end="")
        printCollectionLine(r)
        keysList.append(r)
        count += 1





    #result = db.Keys.find_one({"key_number": key})['key_number']
    #having issues retrieving the key object the user selects
    #db.Keys.remove([{"_id": DBRef("keys", k)}])
    # "room_number": DBRef("Room", chosenRoom["room_number"]),


def deleteEmployee():
    employeeList = []
    allEmployees = db.Employees.find()
    count = 0
    for r in allEmployees:
        print(str(count), ". ", end="")
        printCollectionLine(r)
        employeeList.append(r)
        count += 1

    chosenemployee = employeeList[int(input("Please enter the index of the employee you want to delete: "))]
    db.Employees.delete_one({"_id": chosenemployee["_id"]})
    print("The employee has been deleted\n\n")

    employeeList = []
    allEmployees = db.Employees.find()
    count = 0
    for r in allEmployees:
        print(str(count), ". ", end="")
        printCollectionLine(r)
        employeeList.append(r)
        count += 1


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
            elif choice == 4:
                issueKey()
            elif choice == 5:
                reportLossKey()
            elif choice == 6:
                roomsThatICanEnter()
            elif choice == 7:
                deleteKey()
            elif choice == 8:
                deleteEmployee()
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
