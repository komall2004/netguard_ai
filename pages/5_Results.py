import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Results",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Model Evaluation & Results")

# --------------------------------------------------
# CHECK DATASET
# --------------------------------------------------

if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()

if "detection_result" not in st.session_state:
    st.warning("⚠️ Run Threat Detection first.")
    st.stop()

df = st.session_state["df"]

dataset = st.session_state.get(
    "dataset",
    "Unknown"
)

detection_mode = st.session_state.get(
    "detection_mode"
)

st.info(
    f"📂 Dataset: **{dataset}**  |  "
    f"Records: **{len(df):,}**"
)

# ==================================================
# SINGLE MODEL
# ==================================================

if detection_mode == "Single Model":

    selected_model = st.session_state.get(
        "selected_model"
    )

    if selected_model is None:
        st.warning(
            "⚠️ No model selection found. "
            "Please run the Threat Detection page again."
        )
        st.stop()

    st.subheader(
        f"🧪 Evaluate {selected_model}"
    )

    st.write(
        f"You selected **{selected_model}** "
        "in the Threat Detection page."
    )

    if st.button(
        f"📊 Evaluate {selected_model}",
        width="stretch"
    ):

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        files = {
            "file": (
                "uploaded_dataset.csv",
                csv_data,
                "text/csv"
            )
        }

        try:

            with st.spinner(
                f"🧠 Evaluating {selected_model}..."
            ):

                response = requests.post(
                    "http://127.0.0.1:8000/evaluate",
                    params={
                        "model_name": selected_model
                    },
                    files=files,
                    timeout=900
                )

            if response.status_code == 200:

                result = response.json()
                
                if "error" in result:

                    st.error(
                        result["error"]
                    )

                else:

                    st.session_state[
                        "evaluation_result"
                    ] = result

                    st.success(
                        "✅ Evaluation completed!"
                    )

            else:

                st.error(
                    f"❌ FastAPI error: "
                    f"{response.status_code}"
                )

                st.write(
                    response.text
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Could not connect to FastAPI."
            )

        except requests.exceptions.Timeout:

            st.error(
                "⏳ Evaluation timed out."
            )


# ==================================================
# COMPARE ALL MODELS
# ==================================================

elif detection_mode == "Compare All Models":

    st.subheader(
        "🏆 Evaluate All Models"
    )

    st.write(
        "You selected model comparison, so all three "
        "trained models will be evaluated."
    )

    if st.button(
        "📊 Evaluate All Models",
        width="stretch"
    ):

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        files = {
            "file": (
                "uploaded_dataset.csv",
                csv_data,
                "text/csv"
            )
        }

        try:

            with st.spinner(
                "🧠 Evaluating all three models..."
            ):

                response = requests.post(
                    "http://127.0.0.1:8000/evaluate-comparison",
                    files=files,
                    timeout=900
                )

            if response.status_code == 200:

                result = response.json()

                if "error" in result:

                    st.error(
                        result["error"]
                    )

                else:

                    st.session_state[
                        "evaluation_result"
                    ] = result

                    st.success(
                        "✅ Model evaluation completed!"
                    )

            else:

                st.error(
                    f"❌ FastAPI error: "
                    f"{response.status_code}"
                )

                st.write(
                    response.text
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Could not connect to FastAPI."
            )

        except requests.exceptions.Timeout:

            st.error(
                "⏳ Evaluation timed out."
            )


# ==================================================
# DISPLAY EVALUATION RESULT
# ==================================================

if "evaluation_result" in st.session_state:

    result = st.session_state[
        "evaluation_result"
    ]

    st.divider()

    # --------------------------------------------------
    # SINGLE MODEL RESULT
    # --------------------------------------------------

    if detection_mode == "Single Model":

        st.subheader(
            f"📈 {selected_model} Evaluation"
        )

        # Your /evaluate endpoint returns:
        # accuracy
        # precision
        # recall
        # f1
        # confusion_matrix
        # report

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Accuracy",
                f"{result['accuracy']:.2%}"
            )

        with col2:
            st.metric(
                "Precision",
                f"{result['precision']:.2%}"
            )

        with col3:
            st.metric(
                "Recall",
                f"{result['recall']:.2%}"
            )

        with col4:
            st.metric(
                "F1 Score",
                f"{result['f1']:.2%}"
            )

        st.success(
            f"🤖 Model Evaluated: **{selected_model}**"
        )

        # --------------------------------------------------
        # CONFUSION MATRIX
        # --------------------------------------------------

        st.subheader(
            "🔢 Confusion Matrix"
        )

        cm = pd.DataFrame(
            result["confusion_matrix"],
            index=[
                "Actual Normal",
                "Actual Attack"
            ],
            columns=[
                "Predicted Normal",
                "Predicted Attack"
            ]
        )

        st.dataframe(
            cm,
            width="stretch"
        )

        # --------------------------------------------------
        # CLASSIFICATION REPORT
        # --------------------------------------------------

        st.subheader(
            "📋 Classification Report"
        )

        if "report" in result:

            report = pd.DataFrame(
                result["report"]
            ).transpose()

            st.dataframe(
                report,
                width="stretch"
            )

        # --------------------------------------------------
        # METRIC CHART
        # --------------------------------------------------

        metrics_df = pd.DataFrame({
            "Metric": [
                "Accuracy",
                "Precision",
                "Recall",
                "F1 Score"
            ],

            "Score": [
                result["accuracy"],
                result["precision"],
                result["recall"],
                result["f1"]
            ]
        })

        st.subheader(
            "📊 Performance Metrics"
        )

        st.bar_chart(
            metrics_df.set_index("Metric")
        )


    # --------------------------------------------------
    # COMPARISON RESULT
    # --------------------------------------------------

    elif detection_mode == "Compare All Models":

        st.subheader(
            "🏆 Model Performance Comparison"
        )

        models = result["models"]
        models = result.get("models")

        if models is None:
          st.error("❌ Backend response format is different from what Results page expects.")
          st.json(result)
          st.stop()

        comparison = []

        for model_name, metrics in models.items():

            comparison.append({

                "Model": model_name,

                "Accuracy":
                    metrics["accuracy"],

                "Precision":
                    metrics["precision"],

                "Recall":
                    metrics["recall"],

                "F1 Score":
                    metrics["f1"]

            })

        comparison_df = pd.DataFrame(
            comparison
        )

        st.dataframe(
            comparison_df.style.format({
                "Accuracy": "{:.2%}",
                "Precision": "{:.2%}",
                "Recall": "{:.2%}",
                "F1 Score": "{:.2%}"
            }),
            width="stretch",
            hide_index=True
        )

        # --------------------------------------------------
        # BEST MODEL
        # --------------------------------------------------

        best_model = result["best_model"]

        st.success(
            f"🏆 Best Performing Model: "
            f"**{best_model}**"
        )

        # --------------------------------------------------
        # CHART
        # --------------------------------------------------

        st.subheader(
            "📊 Performance Comparison"
        )

        chart_df = comparison_df.set_index(
            "Model"
        )

        st.bar_chart(
            chart_df[
                [
                    "Accuracy",
                    "Precision",
                    "Recall",
                    "F1 Score"
                ]
            ]
        )

        # --------------------------------------------------
        # CONFUSION MATRICES
        # --------------------------------------------------

        st.subheader(
            "🔢 Confusion Matrices"
        )

        tabs = st.tabs(
            list(models.keys())
        )

        for tab, (model_name, metrics) in zip(
            tabs,
            models.items()
        ):

            with tab:

                cm = pd.DataFrame(
                    metrics["confusion_matrix"],
                    index=[
                        "Actual Normal",
                        "Actual Attack"
                    ],
                    columns=[
                        "Predicted Normal",
                        "Predicted Attack"
                    ]
                )

                st.write(
                    f"### {model_name}"
                )

                st.dataframe(
                    cm,
                    width="stretch"
                )