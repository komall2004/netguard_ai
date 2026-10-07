from fastapi import FastAPI,UploadFile,File
import io
import joblib
from preprocessing_service import analyze_preprocessing
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import pandas as pd
import numpy as np
column_names = [
    "duration", "protocol_type", "service", "flag",
    "src_bytes", "dst_bytes", "land", "wrong_fragment",
    "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root",
    "num_file_creations", "num_shells", "num_access_files",
    "num_outbound_cmds", "is_host_login", "is_guest_login",
    "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate",
    "diff_srv_rate", "srv_diff_host_rate", "dst_host_count",
    "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "label", "difficulty"
]
app=FastAPI(
    title="NetGuard API",
    description="Network Intrusion Detection API",
    version="1.0.0"
    )
svm_model = joblib.load("one_class_svm.pkl")
svm_preprocess = joblib.load("preprocessor.pkl")
isolation_model= joblib.load("isolation_forest.pkl")
isolation_preprocess = joblib.load("isolation_forest_preprocessor.pkl")
lof_model = joblib.load("lof.pkl")
lof_preprocess = joblib.load("lof_preprocessor.pkl")
                         
@app.get("/")
def home():
    return{
        "message":"NetGuard AI Backend is running"
    }

@app.get("/health")
def health():
    return{
        "status":"online"
    }
@app.get("/model-info")
def model_info():
    return {
        "model": "One-Class SVM",
        "learning_type": "Unsupervised",
        "purpose": "Network anomaly detection"
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Check whether the CSV already has column names
    file.file.seek(0)

    header_df = pd.read_csv(file.file, nrows=0)

    expected_columns = set(column_names)

    has_header = len(
        expected_columns.intersection(set(header_df.columns))
    ) > 0

    # Start reading from the beginning again
    file.file.seek(0)

    if has_header:
        chunks = pd.read_csv(
            file.file,
            chunksize=5000
        )
    else:
        chunks = pd.read_csv(
            file.file,
            header=None,
            names=column_names,
            chunksize=5000
        )

    normal_count = 0
    attack_count = 0
    total_records = 0

    for chunk in chunks:

        # Keep label separate if it exists
        actual_labels = None

        if "label" in chunk.columns:
            actual_labels = chunk["label"].copy()

        # Remove columns not used by the model
        X = chunk.drop(
            columns=["label", "difficulty"],
            errors="ignore"
        )

        # Apply saved preprocessing
        X_processed = svm_preprocess.transform(X)

        # Predict
        predictions = svm_model.predict(X_processed)

        # Count results
        normal_count += int((predictions == 1).sum())
        attack_count += int((predictions == -1).sum())

        total_records += len(predictions)

    return {
        "filename": file.filename,
        "total_records": total_records,
        "normal_records": normal_count,
        "attack_records": attack_count
    }
    
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):

#     df = pd.read_csv(file.file)

#     return {
#         "filename": file.filename,
#         "rows": len(df),
#         "columns": len(df.columns)
#     }
@app.post("/evaluate")
async def evaluate(
    file: UploadFile = File(...),
    model_name: str = "One-Class SVM"
):

    contents = await file.read()

    # ---------------------------------------------
    # READ DATASET
    # ---------------------------------------------

    temp_df = pd.read_csv(
        io.BytesIO(contents),
        nrows=0
    )

    has_header = "protocol_type" in temp_df.columns

    if has_header:

        df = pd.read_csv(
            io.BytesIO(contents)
        )

    else:

        df = pd.read_csv(
            io.BytesIO(contents),
            header=None,
            names=column_names
        )

    # ---------------------------------------------
    # CHECK LABEL
    # ---------------------------------------------

    if "label" not in df.columns:

        return {
            "error": "Evaluation requires a labeled dataset."
        }

    # ---------------------------------------------
    # FEATURES + TRUE LABELS
    # ---------------------------------------------

    X = df.drop(
        columns=["label", "difficulty"],
        errors="ignore"
    )

    y_true = df["label"].apply(
        lambda x: 0
        if str(x).lower() == "normal"
        else 1
    )

    # ---------------------------------------------
    # SELECT MODEL
    # ---------------------------------------------

    if model_name == "Isolation Forest":

        X_processed = isolation_preprocess.transform(X)

        predictions = isolation_model.predict(
            X_processed
        )

        predictions = np.where(
            predictions == -1,
            1,
            0
        )

    elif model_name == "Local Outlier Factor":

        X_processed = lof_preprocess.transform(X)

        predictions = lof_model.predict(
            X_processed
        )

        predictions = np.where(
            predictions == -1,
            1,
            0
        )

    elif model_name == "One-Class SVM":

        X_processed = svm_preprocess.transform(X)

        predictions = svm_model.predict(
            X_processed
        )

        predictions = np.where(
            predictions == 1,
            0,
            1
        )

    else:

        return {
            "error": f"Invalid model name: {model_name}"
        }

    # ---------------------------------------------
    # EVALUATION METRICS
    # ---------------------------------------------

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    precision = precision_score(
        y_true,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        predictions,
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        predictions
    )

    report = classification_report(
        y_true,
        predictions,
        output_dict=True,
        zero_division=0
    )

    # ---------------------------------------------
    # RETURN RESULT
    # ---------------------------------------------

    return {
        "model": model_name,
        "rows": len(df),

        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,

        "confusion_matrix": cm.tolist(),

        "report": report
    }
@app.post("/evaluate-comparison")
async def evaluate_comparison(file: UploadFile = File(...)):

    # Read uploaded file once
    contents = await file.read()

    # Detect header
    temp_df = pd.read_csv(
        io.BytesIO(contents),
        nrows=0
    )

    has_header = (
        "protocol_type" in temp_df.columns
    )

    # Read actual dataset
    if has_header:

        df = pd.read_csv(
            io.BytesIO(contents)
        )

    else:

        df = pd.read_csv(
            io.BytesIO(contents),
            header=None,
            names=column_names
        )

    # Evaluation requires labels
    if "label" not in df.columns:

        return {
            "error": "Evaluation requires a labeled dataset."
        }

    # Actual labels
    y_true = df["label"].apply(
        lambda x: 0
        if str(x).lower() == "normal"
        else 1
    )

    X = df.drop(
        columns=["label", "difficulty"],
        errors="ignore"
    )

    results = {}

    # ==================================================
    # ISOLATION FOREST
    # ==================================================

    X_if = isolation_preprocess.transform(X)

    if_predictions = isolation_model.predict(
        X_if
    )

    if_predictions = np.where(
        if_predictions == -1,
        1,
        0
    )

    results["Isolation Forest"] = {
        "accuracy": accuracy_score(
            y_true,
            if_predictions
        ),

        "precision": precision_score(
            y_true,
            if_predictions,
            zero_division=0
        ),

        "recall": recall_score(
            y_true,
            if_predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_true,
            if_predictions,
            zero_division=0
        ),

        "confusion_matrix": confusion_matrix(
            y_true,
            if_predictions
        ).tolist()
    }

    # ==================================================
    # LOF
    # ==================================================

    X_lof = lof_preprocess.transform(X)

    lof_predictions = lof_model.predict(
        X_lof
    )

    lof_predictions = np.where(
        lof_predictions == -1,
        1,
        0
    )

    results["Local Outlier Factor"] = {
        "accuracy": accuracy_score(
            y_true,
            lof_predictions
        ),

        "precision": precision_score(
            y_true,
            lof_predictions,
            zero_division=0
        ),

        "recall": recall_score(
            y_true,
            lof_predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_true,
            lof_predictions,
            zero_division=0
        ),

        "confusion_matrix": confusion_matrix(
            y_true,
            lof_predictions
        ).tolist()
    }

    # ==================================================
    # ONE-CLASS SVM
    # ==================================================

    X_svm = svm_preprocess.transform(X)

    svm_predictions = svm_model.predict(
        X_svm
    )

    svm_predictions = np.where(
        svm_predictions == 1,
        0,
        1
    )

    results["One-Class SVM"] = {
        "accuracy": accuracy_score(
            y_true,
            svm_predictions
        ),

        "precision": precision_score(
            y_true,
            svm_predictions,
            zero_division=0
        ),

        "recall": recall_score(
            y_true,
            svm_predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_true,
            svm_predictions,
            zero_division=0
        ),

        "confusion_matrix": confusion_matrix(
            y_true,
            svm_predictions
        ).tolist()
    }

    # ==================================================
    # FIND BEST MODEL
    # ==================================================

    best_model = max(
        results,
        key=lambda model:
        results[model]["f1"]
    )

    return {
        "filename": file.filename,
        "total_records": len(df),
        "models": results,
        "best_model": best_model
    }
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    # --------------------------------------------------
    # Read the uploaded dataset
    # --------------------------------------------------

    file.file.seek(0)

    df = pd.read_csv(file.file)


    # --------------------------------------------------
    # Missing Values
    # --------------------------------------------------

    missing_values = df.isnull().sum()

    missing_columns = {
        str(column): int(count)
        for column, count in missing_values.items()
        if count > 0
    }


    # --------------------------------------------------
    # Missing Percentage
    # --------------------------------------------------

    missing_percentage = {
        str(column): round(
            (count / len(df)) * 100,
            2
        )
        for column, count in missing_values.items()
        if count > 0
    }


    # --------------------------------------------------
    # Duplicate Rows
    # --------------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )


    # --------------------------------------------------
    # Numerical Columns
    # --------------------------------------------------

    numerical_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()


    # --------------------------------------------------
    # Categorical Columns
    # --------------------------------------------------

    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()


    # --------------------------------------------------
    # Data Types
    # --------------------------------------------------

    data_types = {
        str(column): str(dtype)
        for column, dtype in df.dtypes.items()
    }


    # --------------------------------------------------
    # Return Result
    # --------------------------------------------------

    return {

        "filename": file.filename,

        "rows": len(df),

        "columns": len(df.columns),

        "missing_values": missing_columns,

        "missing_percentage": missing_percentage,

        "duplicate_rows": duplicate_count,

        "numerical_columns": numerical_columns,

        "categorical_columns": categorical_columns,

        "data_types": data_types
    }

@app.post("/preprocessing-recommendations")
async def preprocessing_recommendations(
    file: UploadFile = File(...)
):
    file.file.seek(0)
  
    # Read the uploaded CSV
    header_df = pd.read_csv(file.file,nrows=0)
    expected_columns=set(column_names)
    has_header = len(
            expected_columns.intersection(set(header_df.columns))
        ) > 0
    file.file.seek(0)
        # Read the CSV correctly
    if has_header:
        df = pd.read_csv(file.file)
    else:
        df = pd.read_csv(
                file.file,
                header=None,
                names=column_names
            )

    result = analyze_preprocessing(df)

    return {
        "filename": file.filename,
        "recommendations": result
    }
@app.post("/model-comparison")
async def model_comparison(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    # Handle headerless NSL-KDD
    if "protocol_type" not in df.columns and len(df.columns) == 43:

        df = pd.read_csv(
            io.BytesIO(contents),
            header=None
        )

        df.columns = column_names
    # Remove labels if they exist
    X = df.drop(
        columns=["label", "difficulty"],
        errors="ignore"
    )

    # Isolation Forest
    X_if = isolation_preprocess.transform(X)
    if_predictions = isolation_model.predict(X_if)

    if_predictions = np.where(
        if_predictions == -1,
        1,
        0
    )

    # LOF
    X_lof = lof_preprocess.transform(X)
    lof_predictions = lof_model.predict(X_lof)

    lof_predictions = np.where(
        lof_predictions == -1,
        1,
        0
    )

    # One-Class SVM
    X_svm = svm_preprocess.transform(X)
    svm_predictions = svm_model.predict(X_svm)

    svm_predictions = np.where(
        svm_predictions == 1,
        0,
        1
    )

    return {
        "rows": len(df),

        "isolation_forest": {
            "normal": int((if_predictions == 0).sum()),
            "anomaly": int((if_predictions == 1).sum())
        },

        "lof": {
            "normal": int((lof_predictions == 0).sum()),
            "anomaly": int((lof_predictions == 1).sum())
        },

        "one_class_svm": {
            "normal": int((svm_predictions == 0).sum()),
            "anomaly": int((svm_predictions == 1).sum())
        }
    }
@app.post("/single-model")
async def single_model(
    model_name: str,
    file: UploadFile = File(...)
):
    contents = await file.read()

    df = pd.read_csv(io.BytesIO(contents))

    # Handle headerless NSL-KDD
    if "protocol_type" not in df.columns and len(df.columns) == 43:
        df = pd.read_csv(
            io.BytesIO(contents),
            header=None
        )
        df.columns = column_names

    X = df.drop(
        columns=["label", "difficulty"],
        errors="ignore"
    )

    if model_name == "Isolation Forest":

        X_processed = isolation_preprocess.transform(X)

        predictions = isolation_model.predict(X_processed)

        predictions = np.where(
            predictions == -1,
            1,
            0
        )

    elif model_name == "Local Outlier Factor":

        X_processed = lof_preprocess.transform(X)

        predictions = lof_model.predict(X_processed)

        predictions = np.where(
            predictions == -1,
            1,
            0
        )

    elif model_name == "One-Class SVM":

        X_processed = svm_preprocess.transform(X)

        predictions = svm_model.predict(X_processed)

        predictions = np.where(
            predictions == 1,
            0,
            1
        )

    else:
        return {
            "error": "Invalid model name"
        }

    return {
        "model": model_name,
        "rows": len(df),
        "normal": int((predictions == 0).sum()),
        "anomaly": int((predictions == 1).sum())
    }