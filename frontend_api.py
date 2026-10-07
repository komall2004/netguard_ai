import requests


API_URL = "http://127.0.0.1:8000"


def send_to_backend(endpoint, df):

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

    response = requests.post(
        f"{API_URL}{endpoint}",
        files=files
    )

    return response