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
            "_id": "$type_data.dispo_data.dispo",
            "count": {"$sum": "$type_data.dispo_data.count"},
        }
    },
    {"$sort": {"_id": -1}},
]
result = list(collection.aggregate(pipeline))

labels = ["Oui", "Non"]
match len(result):
    case 0:
        raise ValueError("Void data")
    case 1:
        if result[0]["_id"] == True:
            counts = [result[0]["count"], 0]
        else:
            counts = [0, result[0]["count"]]
    case 2:
        counts = [entry["count"] for entry in result]


def func(pct, allvals):
    absolute = int(np.round(pct / 100.0 * np.sum(allvals)))
    return f"{pct:.1f}%\n({absolute:d})"


fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(aspect="equal"))
wedges, texts, autotexts = ax.pie(
    counts,
    labels=labels,
    autopct=lambda pct: func(pct, counts),
    colors=["green", "red"],
    textprops=dict(color="w"),
)
ax.legend(
    wedges,
    labels,
    title="Fontaine disponible",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1),
)

plt.setp(autotexts, size=9, weight="bold")

st.write("# Disponibilité globale des fontaines à boire")

st.pyplot(fig)
