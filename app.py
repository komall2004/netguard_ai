import streamlit as st
st.set_page_config(
    page_title="NetGuard AI",
    page_icon="🛡️",
    layout="wide"
)
st.title("🛡️ NetGuard AI")
st.subheader("AI-Powered Network Intrusion Detection System")
st.markdown(""" 
**NetGuard AI** is an intelligent cybersecurity application that detects anomalous
and malicious network traffic using unsupervised machine learning techniques.

The system allows users to:

- 📂 Upload network traffic datasets
- 📊 Analyze dataset statistics
- 🧹 Preprocess data automatically
- 🛡️ Detect anomalies using AI models
- 📈 Compare multiple detection algorithms
- 🏆 View detailed performance reports""")

st.subheader("🤖 Supported Detection Models")

st.markdown("""
- 🌲 **Isolation Forest**
- 📍 **Local Outlier Factor (LOF)**
- 🎯 **One-Class SVM**
""")

st.divider()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Detection Models", "3")

with col2:
    st.metric("Learning Type", "Unsupervised")

with col3:
    st.metric("Workflow", "End-to-End")

with col4:
    if "dataset" in st.session_state:
        st.metric("Dataset", st.session_state["dataset"])
    else:
        st.metric("Dataset", "Not Loaded")

st.divider()

left, right = st.columns(2)

with left:

    st.subheader("🚀 Core Features")

    st.markdown("""
✔ Automatic Dataset Detection

✔ Dataset Analysis

✔ Intelligent Data Preprocessing

✔ Missing Value Handling

✔ Encoding & Scaling Recommendations

✔ Threat Detection

✔ Model Comparison

✔ Performance Reporting
""")

with right:

    st.subheader("🤖 Detection Models")

    st.markdown("""
### 🌲 Isolation Forest
Tree-based anomaly detection suitable for large-scale network traffic.

### 📍 Local Outlier Factor
Detects anomalies by comparing local neighborhood density.

### 🎯 One-Class SVM
Learns normal network behavior and identifies previously unseen attacks.
""")

st.divider()
st.subheader("⚙ Detection Workflow")

workflow1, workflow2, workflow3, workflow4, workflow5 = st.columns(5)

workflow1.success("📂\n\nUpload")
workflow2.info("📊\n\nAnalyze")
workflow3.warning("🧹\n\nPreprocess")
workflow4.error("🛡️\n\nDetect")
workflow5.success("📈\n\nResults")

st.divider()

st.subheader("🏆 Project Highlights")

st.markdown("""
- Supports NSL-KDD and compatible intrusion detection datasets

- Intelligent preprocessing recommendations

- Compare Isolation Forest, LOF and One-Class SVM

- Interactive performance dashboard

- Designed for cybersecurity analytics
""")

st.divider()

if "dataset" in st.session_state:
    st.success(
        f"Dataset detected: **{st.session_state['dataset']}**\n\nUse the sidebar to continue the analysis."
    )
else:
    st.info(
        "👈 Upload a supported intrusion detection dataset using the sidebar to begin."
    )

st.caption("NetGuard AI • Built using Streamlit • Scikit-learn • Python")