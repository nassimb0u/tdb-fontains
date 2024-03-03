import streamlit as st
from pymongo import MongoClient

st.set_page_config(
    page_title="TDB Fontaines",
    page_icon="💧",
)


if "collection" not in st.session_state:
    connection_string = "mongodb://test-projet-sds:test-projet-sds@localhost:27017/?authSource=projet-sds"
    client = MongoClient(connection_string)
    db = client["projet-sds"]
    st.session_state.collection = db["aggregated_data"]

st.write("# Tableau de bord des fontaines à boire de Paris")

st.sidebar.success("Sélectionnez un graphique ci-dessus")

st.markdown(
    """
### [Source de données](https://opendata.paris.fr/explore/dataset/fontaines-a-boire)

**Eau de Paris** veille à favoriser l’accès à l’eau pour tous en gérant notamment une partie de l’important réseau des 1 200 points d’eau dans les rues, les parcs et les bois : fontaines Wallace, du Millénaire, à l’Albien, Pétillante, Totem, bornes fontaines dans les jardins publics, points d’eau aux sanisettes…

Afin de garantir un accès à l’eau dans toute la ville, **Eau de Paris** a en charge les 190 fontaines à boire de la capitale situées sur la voie publique (Wallace, Millénaire, bornes fontaines, "Pétillante", "Poings d'eau", à l'Albien, "Totems" et "Arceaux") ainsi que les 335 points d’eau situés dans les parcs et espaces verts. En partenariat avec les services sociaux, l’entreprise a identifié une soixantaine de fontaines à maintenir ouvertes toute l’année, même en période de gel – sauf cas extrême –, afin de permettre aux sans-abri d’accéder à la ressource.
"""
)
