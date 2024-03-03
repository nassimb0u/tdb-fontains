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
            "_id": {"commune": "$_id", "type_objet": "$type_data.type_objet"},
            "count": {"$sum": "$type_data.dispo_data.count"},
        }
    },
    {"$sort": {"_id.type_objet": 1}},
    {
        "$group": {
            "_id": "$_id.commune",
            "type_data": {
                "$push": {"type_objet": "$_id.type_objet", "count": "$count"}
            },
        }
    },
    {"$sort": {"_id": 1}},
]
result = list(collection.aggregate(pipeline))


categories = sorted(collection.distinct("type_data.type_objet"))
counts = {}

for item in result:
    commune_tokens = item["_id"].split()
    if len(commune_tokens) > 2:
        commune = commune_tokens[1]
    else:
        commune = item["_id"]

    counts[commune] = []

    i = 0
    for category in categories:
        if (
            i < len(item["type_data"])
            and item["type_data"][i]["type_objet"] == category
        ):
            counts[commune].append(item["type_data"][i]["count"])
            i += 1
        else:
            counts[commune].append(0)


labels = list(counts.keys())
data = np.array(list(counts.values()))
data_cum = data.cumsum(axis=1)
# category_colors = plt.colormaps["RdYlGn"](np.linspace(0.15, 0.85, data.shape[1]))

fig, ax = plt.subplots(figsize=(8, 10))
ax.invert_yaxis()
# ax.xaxis.set_visible(False)
ax.set_xlim(0, np.sum(data, axis=1).max() + 2)

for i, colname in enumerate(categories):
    widths = data[:, i]
    starts = data_cum[:, i] - widths
    rects = ax.barh(labels, widths, left=starts, height=0.6, label=colname)
    # r, g, b, _ = color
    # text_color = "white" if r * g * b < 0.5 else "darkgrey"
    # ax.bar_label(rects, label_type="center", color=text_color)
ax.legend(
    ncols=3,
    bbox_to_anchor=(0, 1),
    loc="lower left",
    title="Type de fontaines",
)

ax.set_xlabel("Nombre de fontaines")
ax.set_ylabel("Commune")

st.write("# Types de fontaines à boire par commune")

st.pyplot(fig)
