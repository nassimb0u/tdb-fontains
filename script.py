import os
import json
from pathlib import Path
from datetime import datetime

from pymongo import MongoClient

# setup mongo connection
connection_string = (
    "mongodb://test-projet-sds:test-projet-sds@localhost:27017/?authSource=projet-sds"
)
client = MongoClient(connection_string)
db = client["projet-sds"]
raw_collection = db["raw_data"]

# read raw data and store what matter to mongo
data_dir_path = "drinking_fontains_data/"
file_names = os.listdir(data_dir_path)
for file_name in file_names:
    file_path = os.path.join(data_dir_path, file_name)
    timestamp = datetime.fromisoformat(Path(file_path).stem.split()[-1])
    with open(file_path) as file:
        data = json.load(file)
    for item in data:
        document = {}
        document["updatedAt"] = timestamp
        document["commune"] = item["commune"]
        document["type_objet"] = item["type_objet"]
        document["dispo"] = True if item["dispo"] == "OUI" else False
        query = {"_id": item["gid"]}
        existing_document = raw_collection.find_one(query)
        if existing_document:
            raw_collection.update_one(query, {"$set": document})
        else:
            document["_id"] = item["gid"]
            document["createdAt"] = timestamp
            raw_collection.insert_one(document)
    try:
        os.remove(file_path)
    except OSError as e:
        print(f"Error deleting '{file_path}': {e}")

# do aggregations using mongo engine and store them to mongo
pipeline = [
    {
        "$group": {
            "_id": {
                "commune": "$commune",
                "type_objet": "$type_objet",
                "dispo": "$dispo",
            },
            "count": {"$sum": 1},
        }
    },
    {
        "$group": {
            "_id": {"commune": "$_id.commune", "type_objet": "$_id.type_objet"},
            "nested_groups": {"$push": {"dispo": "$_id.dispo", "count": "$count"}},
        }
    },
    {
        "$group": {
            "_id": "$_id.commune",
            "type_data": {
                "$push": {
                    "type_objet": "$_id.type_objet",
                    "dispo_data": "$nested_groups",
                }
            },
        }
    },
    {"$out": "aggregated_data"},
]

raw_collection.aggregate(pipeline)

client.close()
