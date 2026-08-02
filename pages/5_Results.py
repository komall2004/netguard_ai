import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if "results" not in st.session_state:
    st.warning("⚠ Run a model first.")
    st.stop()
results=st.session_state["results"]

# if results["accuracy"] > 0.80:
#     st.success("The selected model achieved strong overall detection performance.")

# if results["recall"] > 0.95:
#     st.success("Excellent attack recall. Most malicious traffic was detected.")

# if results["precision"] < 0.70:
#     st.warning("Some normal traffic was classified as attacks, indicating a higher false positive rate.")

# col1,col2,col3,col4=st.columns(4)
# with col1:
#     st.metric("Accuracy",f"{results['accuracy']:.2%}")
# with col2:
#     st.metric("Precision",f"{results['precision']:.2%}")
# with col3:
#     st.metric("Recall",f"{results['recall']:.2%}")
# with col4:
#     st.metric("F1",f"{results['f1']:.2%}")

# st.subheader("Confusion Matrix")
# cm=pd.DataFrame(
#     results["confusion_matrix"],
#     index=["Normal","Attack"],
#     columns=["Pred Normal","Pred Attack"]
# )
# st.dataframe(cm,use_container_width=True)
# st.subheader("Classification Report")

# report = pd.DataFrame(results["report"]).transpose()

# st.dataframe(report, use_container_width=True)

if results.get("type") == "comparison":

    st.title("🏆 Model Comparison")

    st.dataframe(
        results["comparison"],
        use_container_width=True
    )
    st.bar_chart(
    results["comparison"].set_index("Model")["Accuracy"] * 100
)

    best = results["best_model"]

    st.success(
        f"""
🏆 Best Model: {best['Model']}

Accuracy: {best['Accuracy']:.2%}
"""
    )

    st.stop()
st.title("📈 Detection Results")

if results["accuracy"] > 0.80:
    st.success("The selected model achieved strong overall detection performance.")

if results["recall"] > 0.95:
    st.success("Excellent attack recall. Most malicious traffic was detected.")

if results["precision"] < 0.70:
    st.warning("Some normal traffic was classified as attacks, indicating a higher false positive rate.")

col1,col2,col3,col4=st.columns(4)
with col1:
    st.metric("Accuracy",f"{results['accuracy']:.2%}")
with col2:
    st.metric("Precision",f"{results['precision']:.2%}")
with col3:
    st.metric("Recall",f"{results['recall']:.2%}")
with col4:
    st.metric("F1",f"{results['f1']:.2%}")

st.success(f"Model Used: {results['model']}")
st.subheader("Confusion Matrix")
cm=pd.DataFrame(
    results["confusion_matrix"],
    index=["Normal","Attack"],
    columns=["Pred Normal","Pred Attack"]
)
st.dataframe(cm,use_container_width=True)
st.subheader("Classification Report")

report = pd.DataFrame(results["report"]).transpose()

st.dataframe(report, use_container_width=True)
metrics = pd.DataFrame({
    "Metric": ["Accuracy", "Precision", "Recall", "F1"],
   "Score": [
        results["accuracy"] * 100,
        results["precision"] * 100,
        results["recall"] * 100,
        results["f1"] * 100
   ]
})

st.bar_chart(metrics.set_index("Metric"))