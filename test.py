import requests
import streamlit as st

uploaded_file = st.file_uploader(
    "Upload Dataset",
    type=["csv"]
)
if uploaded_file is not None:

    st.success("Dataset uploaded successfully!")

    if st.button("Analyze Dataset"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "text/csv"
            )
        }

        response = requests.post(
            "http://127.0.0.1:8000/analyze",
            files=files
        )

        if response.status_code == 200:

            result = response.json()

            st.success("✅ FastAPI backend connected!")

            st.json(result)

        else:

            st.error(
                f"Backend error: {response.status_code}"
            )

            st.write(response.text)
