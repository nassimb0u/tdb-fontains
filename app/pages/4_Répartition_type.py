import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

collection = st.session_state.collection

pipeline = [
    {"$unwind": "$type_data"},
    {"$unwind": "$type_data.dispo_data"},
    {
        "$group": {
            "_id": "$type_data.type_objet",
            "count": {"$sum": "$type_data.dispo_data.count"},
        }
    },
    {"$sort": {"_id": 1}},
]
result = list(collection.aggregate(pipeline))

labels = []
counts = []

for item in result:
    labels.append(item["_id"])
    counts.append(item["count"])


def func(pct, allvals):
    absolute = int(np.round(pct / 100.0 * np.sum(allvals)))
    if pct > 5:
        return f"{pct:.1f}%\n({absolute:d})"
    if pct > 1:
        return f"{pct:.1f}%"
    return ""


fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(aspect="equal"))
wedges, texts, autotexts = ax.pie(
    counts,
    labels=labels,
    autopct=lambda pct: func(pct, counts),
    textprops=dict(color="w"),
)
ax.legend(
    wedges,
    labels,
    title="Type de fontaine",
    loc="center left",
    bbox_to_anchor=(1, 0, 0.5, 1),
)

plt.setp(autotexts, size=9, weight="bold")

st.write("# Répartition des fontaines à boire par type")

st.pyplot(fig)
