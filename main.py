from pymongo import MongoClient
from pymongo import collection
import pymongo

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


if __name__ == "__main__":
    db = setup()
    print('In main: ', db.list_collection_names())
    buildings : collection = db.Buildings

    buildings.delete_many({})
    buildings.create_index([("building_name", pymongo.ASCENDING)], unique=True)
    result = buildings.insert_many([
        {"building_name": "VEC"},
        {"building_name": "ECS"},
        {"building_name": "HC"},
        {"building_name": "HS"},
        {"building_name": "LH"},
        {"building_name": "FA1"},
        {"building_name": "SSSC"},
        {"building_name": "BMAC"}
    ])

    printTable(buildings)