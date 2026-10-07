import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

from model_service import train_one_class_svm,predict


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


df = pd.read_csv(
    r"C:\Users\PARMOD\learn_python\practice\KDDTrain+.csv",
    header=None,
    names=column_names
)


X = df.drop(columns=["label", "difficulty"])

y = df["label"].apply(
    lambda x: 0 if str(x).lower() == "normal" else 1
)


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


categorical = [
    "protocol_type",
    "service",
    "flag"
]

numerical = X.select_dtypes(
    exclude="object"
).columns


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


model, preprocess = train_one_class_svm(
    X_train,
    y_train,
    preprocess
)
predictions = predict(
    model,
    preprocess,
    X_test
)

print("Model trained successfully!")
print("Prediction completed!")

print("Total predictions:", len(predictions))
print("Normal:", np.sum(predictions == 0))
print("Attack:", np.sum(predictions == 1))