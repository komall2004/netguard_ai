import streamlit as st
import pandas as pd
st.title("📂 Upload Dataset")
uploaded_file=st.file_uploader(
    "Choose a file",
    type=["csv"]
)
column_names = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes",
    "land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count",
    "dst_host_srv_count","dst_host_same_srv_rate",
    "dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate",
    "dst_host_srv_serror_rate","dst_host_rerror_rate",
    "dst_host_srv_rerror_rate","label","difficulty"
]

def detect_dataset(uploaded_file):
    df = pd.read_csv(uploaded_file)
    if "protocol_type" in df.columns:
        dataset = "NSL-KDD"
            # return "NSL-KDD"
    elif ("label" in df.columns) or ("Label" in df.columns):
        df.rename(columns={"Label":"label"}, inplace=True)
        dataset= "CIC-IDS2017"
    elif "attack_cat" in df.columns:
        df.rename(columns={"attack_cat":"label"}, inplace=True)
        dataset= "UNSW-NB15"
    else:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file,header=None)
        if df.shape[1]==43 :
            df.columns=column_names
            dataset= "NSL-KDD_NO_HEADER"
        else:
            dataset="Unknown"
    return df, dataset

if uploaded_file is not None:
    # df = pd.read_csv(uploaded_file)
    df,dataset = detect_dataset(uploaded_file)
    st.caption(f"📄 Uploaded File: {uploaded_file.name}")
    size=uploaded_file.size/1024
    st.caption(f"📦 File Size: {size:.2f} KB")
    # df=pd.read_csv(uploaded_file,header=None)
    st.session_state["df"]=df
    st.session_state["dataset"] = dataset

    st.success("✅ Dataset uploaded successfully!")
    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head())