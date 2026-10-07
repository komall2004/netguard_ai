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

    uploaded_file.seek(0)

    # First read normally
    df = pd.read_csv(uploaded_file)

    # --------------------------------------------------
    # NSL-KDD WITH HEADER
    # --------------------------------------------------

    if "protocol_type" in df.columns:

        return df, "NSL-KDD"


    # --------------------------------------------------
    # CIC-IDS2017
    # --------------------------------------------------

    if "label" in df.columns or "Label" in df.columns:

        df.rename(
            columns={"Label": "label"},
            inplace=True
        )

        return df, "CIC-IDS2017"


    # --------------------------------------------------
    # UNSW-NB15
    # --------------------------------------------------

    if "attack_cat" in df.columns:

        df.rename(
            columns={"attack_cat": "label"},
            inplace=True
        )

        return df, "UNSW-NB15"


    # --------------------------------------------------
    # HEADERLESS NSL-KDD
    # --------------------------------------------------

    if len(df.columns) == 43:

        # Check whether the first row actually
        # looks like NSL-KDD data

        first_row = df.iloc[0].astype(str).tolist()

        if (
            len(first_row) > 1
            and first_row[1] in ["tcp", "udp", "icmp"]
        ):

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                header=None,
                names=column_names
            )

            return df, "NSL-KDD_NO_HEADER"


    # --------------------------------------------------
    # GENERIC CSV DATASET
    # --------------------------------------------------

    return df, "Unknown"

if uploaded_file is not None:

    df, dataset = detect_dataset(uploaded_file)

    st.caption(f"📄 Uploaded File: {uploaded_file.name}")

    size = uploaded_file.size / 1024

    st.caption(f"📦 File Size: {size:.2f} KB")

    # Save dataset
   # ============================================================
# SAVE NEW DATASET
# ============================================================

    st.session_state["df"] = df.copy()
    st.session_state["dataset"] = dataset
    st.session_state["filename"] = uploaded_file.name

# Clear results belonging to previous dataset
    st.session_state.pop("analysis_result", None)
    st.session_state.pop("preprocessing_result", None)
    st.session_state.pop("cleaned_df", None)

    st.session_state.pop("detection_result", None)
    st.session_state.pop("detection_mode", None)
    st.session_state.pop("selected_model", None)
    st.session_state.pop("evaluation_result", None)

    st.success("✅ Dataset uploaded successfully!")

#     st.write(
#     f"**Loaded dataset:** {df.shape[0]} rows × {df.shape[1]} columns"
# )

#     st.write(
#     f"**Missing values:** {df.isnull().sum().sum()}"
# )

elif "df" in st.session_state:

    # Dataset was already uploaded earlier
    df = st.session_state["df"]

    dataset = st.session_state.get(
        "dataset",
        "Unknown"
    )

    st.info(
        f"📂 Dataset already loaded: "
        f"{st.session_state.get('filename', 'Uploaded dataset')}"
    )

else:

    st.info("👆 Please upload a dataset to begin.")
    st.stop()


# Show preview for both new and existing datasets
st.subheader("📄 Dataset Preview")

st.dataframe(
    df.head(),
    width="stretch"
)
# st.write("### DEBUG - Upload Page")
# st.write("Filename:", st.session_state.get("filename"))
# st.write("Shape:", st.session_state["df"].shape)
# st.write(
#     "Missing values:",
#     st.session_state["df"].isnull().sum().sum()
# )