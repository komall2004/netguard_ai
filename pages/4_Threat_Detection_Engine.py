import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Threat Detection Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Threat Detection Engine")
st.write(
    "Run trained anomaly detection models on the uploaded network traffic dataset."
)

# --------------------------------------------------
# CHECK DATASET
# --------------------------------------------------

if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()

df = st.session_state["df"]

st.subheader("📊 Dataset Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Rows", df.shape[0])

with col2:
    st.metric("Columns", df.shape[1])

with col3:
    st.metric(
        "Missing Values",
        int(df.isnull().sum().sum())
    )

dataset = st.session_state.get("dataset", "Unknown")

st.info(f"📂 Detected Dataset: **{dataset}**")

# --------------------------------------------------
# DETECTION MODE
# --------------------------------------------------

st.subheader("🤖 Detection Mode")

mode = st.radio(
    "Choose Detection Mode",
    [
        "Single Model",
        "Compare All Models"
    ],
    horizontal=True
)

# --------------------------------------------------
# SINGLE MODEL
# --------------------------------------------------

if mode == "Single Model":

    st.subheader("🎯 Select Detection Model")

    model = st.selectbox(
        "Choose Model",
        [
            "Isolation Forest",
            "Local Outlier Factor",
            "One-Class SVM"
        ]
    )

    st.divider()

    # ----------------------------------------------
    # MODEL INFORMATION
    # ----------------------------------------------

    if model == "Isolation Forest":

        st.subheader("🌲 Isolation Forest")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Number of Trees", "50")

        with col2:
            st.metric("Max Samples", "2048")

        with col3:
            st.metric("Contamination", "0.50")

        st.info(
            "Using the optimized trained Isolation Forest model."
        )

    elif model == "Local Outlier Factor":

        st.subheader("📍 Local Outlier Factor")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Neighbors", "40")

        with col2:
            st.metric("Contamination", "0.50")

        st.info(
            "Using the optimized trained LOF model."
        )

    elif model == "One-Class SVM":

        st.subheader("🎯 One-Class SVM")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Kernel", "RBF")

        with col2:
            st.metric("Gamma", "0.1")

        with col3:
            st.metric("Nu", "0.30")

        st.info(
            "Using the optimized trained One-Class SVM model."
        )


# --------------------------------------------------
# COMPARE ALL MODELS
# --------------------------------------------------

else:

    st.subheader("🏆 Model Comparison")

    st.info(
        """
The following optimized trained models will be evaluated:

🌲 Isolation Forest  
📍 Local Outlier Factor  
🎯 One-Class SVM
"""
    )

    comparison_config = pd.DataFrame({
        "Model": [
            "Isolation Forest",
            "Local Outlier Factor",
            "One-Class SVM"
        ],

        "Configuration": [
            "50 trees | 2048 samples | contamination 0.50",
            "40 neighbors | contamination 0.50",
            "RBF | gamma 0.1 | nu 0.30"
        ]
    })

    st.dataframe(
        comparison_config,
        width="stretch",
        hide_index=True
    )


st.divider()

# --------------------------------------------------
# RUN DETECTION
# --------------------------------------------------

if st.button(
    "🚀 Run Detection",
    width="stretch"
):

    csv_data = df.to_csv(index=False).encode("utf-8")

    files = {
        "file": (
            "uploaded_dataset.csv",
            csv_data,
            "text/csv"
        )
    }

    try:

        with st.spinner(
            "🧠 Running anomaly detection..."
        ):

            # ------------------------------------------
            # SINGLE MODEL
            # ------------------------------------------

            if mode == "Single Model":

                response = requests.post(
                    "http://127.0.0.1:8000/single-model",
                    params={
                        "model_name": model
                    },
                    files=files,
                    timeout=900
                )

            # ------------------------------------------
            # ALL MODELS
            # ------------------------------------------

            else:

                response = requests.post(
                    "http://127.0.0.1:8000/model-comparison",
                    files=files,
                    timeout=900
                )


        # ------------------------------------------
        # SUCCESS
        # ------------------------------------------

        if response.status_code == 200:

            result = response.json()

            st.session_state["detection_result"] = result
            st.session_state["detection_mode"] = mode
            if mode == "Single Model":
               st.session_state["selected_model"] = model

            st.success(
                "✅ Threat detection completed successfully!"
            )

        else:

            st.error(
                f"❌ FastAPI error: {response.status_code}"
            )

            st.write(response.text)


    except requests.exceptions.ConnectionError:

        st.error(
            "❌ Could not connect to FastAPI."
        )

        st.info(
            "Make sure FastAPI is running on port 8000."
        )


    except requests.exceptions.Timeout:

        st.error(
            "⏳ Detection is taking longer than expected."
        )

        st.info(
            "The backend is processing the dataset. "
            "Please try again if the request did not finish."
        )


# --------------------------------------------------
# DISPLAY SINGLE MODEL RESULT
# --------------------------------------------------

if (
    "detection_result" in st.session_state
    and st.session_state.get("detection_mode") == "Single Model"
):

    result = st.session_state["detection_result"]

    st.divider()

    st.subheader("📈 Detection Result")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Model",
             model
        )

    with col2:
        st.metric(
            "Normal Traffic",
            result.get("normal", 0)
        )

    with col3:
        st.metric(
            "Anomalies",
            result.get("anomaly", 0)
        )

    # ----------------------------------------------
    # ANOMALY PERCENTAGE
    # ----------------------------------------------

    total = result.get("normal", 0) + result.get("anomaly", 0)

    if total > 0:
     anomaly_percentage = (
        result.get("anomaly", 0) / total * 100
    )

     st.subheader("🚨 Anomaly Rate")

     st.metric(
        "Detected Anomalies",
        f"{anomaly_percentage:.2f}%"
    )

     st.progress(anomaly_percentage / 100)

# --------------------------------------------------
# DISPLAY COMPARISON RESULT
# --------------------------------------------------

if (
    "detection_result" in st.session_state
    and st.session_state.get("detection_mode") == "Compare All Models"
):

    result = st.session_state["detection_result"]

    st.divider()

    st.subheader("🏆 Model Comparison Results")

    comparison_data = []

    model_mapping = {
        "Isolation Forest": "isolation_forest",
        "Local Outlier Factor": "lof",
        "One-Class SVM": "one_class_svm"
    }

    for model_name, key in model_mapping.items():

        model_result = result.get(key, {})

        normal = model_result.get("normal", 0)
        anomaly = model_result.get("anomaly", 0)

        total = normal + anomaly

        if total > 0:
            anomaly_rate = anomaly / total * 100
        else:
            anomaly_rate = 0

        comparison_data.append({
            "Model": model_name,
            "Normal Traffic": normal,
            "Anomalies": anomaly,
            "Anomaly Rate": f"{anomaly_rate:.2f}%"
        })

    comparison_df = pd.DataFrame(comparison_data)

    st.dataframe(
        comparison_df,
        width="stretch",
        hide_index=True
    )