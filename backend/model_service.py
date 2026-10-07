import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.svm import OneClassSVM


def prepare_data(df):

    # Separate features and label
    X = df.drop(
        columns=["label", "difficulty"],
        errors="ignore"
    )

    y = df["label"].apply(
        lambda x: 0 if str(x).lower() == "normal" else 1
    )

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    # Identify columns
    categorical = [
        "protocol_type",
        "service",
        "flag"
    ]

    numerical = X.select_dtypes(
        exclude="object"
    ).columns.tolist()

    # Create preprocessing object
    preprocess = ColumnTransformer(
        transformers=[
            (
                "num",
                RobustScaler(),
                numerical
            ),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                categorical
            )
        ]
    )

    return X_train, X_test, y_train, y_test, preprocess


def train_one_class_svm(X_train, y_train, preprocess):

    # Keep only normal traffic
    X_train_normal = X_train[y_train == 0]

    # Learn preprocessing from normal traffic
    preprocess.fit(X_train_normal)

    # Transform normal training traffic
    X_train_processed = preprocess.transform(
        X_train_normal
    )

    # Create One-Class SVM
    model = OneClassSVM(
        kernel="rbf",
        gamma=0.1,
        nu=0.30
    )

    # Train model
    model.fit(X_train_processed)

    return model, preprocess


def predict(model, preprocess, X):

    # Apply the SAME preprocessing
    X_processed = preprocess.transform(X)

    # Predict
    predictions = model.predict(X_processed)

    # Convert:
    # +1 → normal → 0
    # -1 → attack → 1

    predictions = np.where(
        predictions == 1,
        0,
        1
    )

    return predictions