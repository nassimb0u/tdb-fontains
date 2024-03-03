import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from pymongo import MongoClient


if "collection" not in st.session_state:
    connection_string = "mongodb://test-projet-sds:test-projet-sds@localhost:27017/?authSource=projet-sds"
    client = MongoClient(connection_string)
    db = client["projet-sds"]
    st.session_state.collection = db["aggregated_data"]

collection = st.session_state.collection

pipeline = [
    {"$unwind": "$type_data"},
    {"$unwind": "$type_data.dispo_data"},
    {
        "$group": {
            "_id": {"commune": "$_id", "dispo_data": "$type_data.dispo_data.dispo"},
            "count": {"$sum": "$type_data.dispo_data.count"},
        }
    },
    {"$sort": {"_id.dispo_data": -1}},
    {
        "$group": {
            "_id": "$_id.commune",
            "dispo_data": {"$push": {"dispo": "$_id.dispo_data", "count": "$count"}},
        }
    },
    {"$sort": {"_id": 1}},
]
result = list(collection.aggregate(pipeline))

categories = ["Oui", "Non"]
counts = {}
for item in result:
    commune_tokens = item["_id"].split()
    if len(commune_tokens) > 2:
        commune = commune_tokens[1]
    else:
        commune = item["_id"]
    match len(item["dispo_data"]):
        case 0:
            counts[commune] = [0, 0]
        case 1:
            if item["dispo_data"][0]["dispo"] == True:
                counts[commune] = [item["dispo_data"][0]["count"], 0]
            else:
                counts[commune] = [0, item["dispo_data"][0]["count"]]
        case 2:
            counts[commune] = [
                item["dispo_data"][0]["count"],
                item["dispo_data"][1]["count"],
            ]

labels = list(counts.keys())
data = np.array(list(counts.values()))
data_cum = data.cumsum(axis=1)
category_colors = ["green", "red"]

fig, ax = plt.subplots(figsize=(6, 8))
ax.invert_yaxis()
# ax.xaxis.set_visible(False)
ax.set_xlim(0, np.sum(data, axis=1).max() + 2)

for i, (colname, color) in enumerate(zip(categories, category_colors)):
    widths = data[:, i]
    starts = data_cum[:, i] - widths
    rects = ax.barh(labels, widths, left=starts, height=0.6, label=colname, color=color)
    ax.bar_label(rects, label_type="center", color="white")
ax.legend(
    ncols=len(categories),
    bbox_to_anchor=(0, 1),
    loc="lower left",
    title="Fontaine disponible",
)
ax.set_xlabel("Nombre de fontaines")
ax.set_ylabel("Commune")

st.write("# Disponibilité des fontaines à boire par commune")

st.pyplot(fig)
