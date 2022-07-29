from io import StringIO, BytesIO
import json
from time import time
import streamlit as st
import pandas as pd
from firebase_admin import credentials, firestore, auth, initialize_app


def export_collection(db, coll_id):
    st.write(f"Exporting collection: {coll_id}...")
    df = pd.DataFrame([dict(row_id=x.id,**x.to_dict()) for x in db.collection(coll_id).get()])
    date_columns = df.select_dtypes(include=['datetime64[ns, UTC]']).columns
    for date_column in date_columns:
        df[date_column] = df[date_column].dt.date

    bio = BytesIO()
    contents = df.to_excel(bio, index=False, engine="xlsxwriter")
    st.write("Export file is ready...")
    st.download_button('Download file', bio.getvalue(), file_name=f"collection_{coll_id}.xlsx")



st.title("NYATApp exporter")

uploaded_file = st.file_uploader("Choose a file")

db = st.session_state.get("db", None) 
app = st.session_state.get("app", None)

if uploaded_file is not None:

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    config = json.load(stringio)

    cred = credentials.Certificate(config)
    
    if st.session_state.get("lastly_used_filename", None) != uploaded_file.name or not app:
        app = initialize_app(cred, name=f"v_{int(time())}")
        st.session_state["app"] = app
        st.session_state["lastly_used_filename"] = uploaded_file.name
    st.write(f"Project has been initialized: {app.project_id} {app.name}")
    db = firestore.client(app)
    st.session_state["db"] = db

if db:
    collections = [x.id for x in db.collections()]

    st.write(f"Collections: {collections}")
    
    selected_coll = st.selectbox("Selected collection", collections)

    if st.button(f"Export collection '{selected_coll}'"):
        export_collection(db, selected_coll)

else:
    st.write("You have to load a config file first")