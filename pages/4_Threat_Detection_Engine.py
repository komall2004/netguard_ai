import streamlit as st
import pandas as pd
import numpy as np
from sklearn.svm import OneClassSVM
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler,OneHotEncoder

st.set_page_config(
    page_title="Threat Detection Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Threat Detection Engine")
st.write("Run anomaly detection models on the uploaded network traffic dataset.")

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

if "cleaned_df" in st.session_state:
        df=st.session_state["cleaned_df"]
elif "df" in st.session_state:
        df = st.session_state["df"]
else:
    st.warning("Upload Dataset First")
    st.stop()

st.subheader("📊 Dataset Status")
col1,col2,col3=st.columns(3)
with col1:
       st.metric("Rows",df.shape[0])
with col2:
       st.metric("Columns",df.shape[1])
with col3:
       st.metric("Missing Values", df.isnull().sum().sum())

if "label" in df.columns:
      target = "label"
      st.success(f"Target Column Detected: {target}")
else:
    st.error("No label column found.")
    st.stop()

X = df.drop(columns=["label", "difficulty"], errors="ignore")

y = df["label"]
y_binary = y.apply(
    lambda x: 0 if str(x).lower() == "normal" else 1
)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_binary,
    test_size=0.2,
    stratify=y_binary,
    random_state=42
)

categorical=['protocol_type', 'service', 'flag']
numerical=X.select_dtypes(exclude="object").columns
preprocess=ColumnTransformer(
    transformers=[("num",RobustScaler(),numerical),("cat",OneHotEncoder(handle_unknown="ignore"),categorical)])
preprocess.fit(X_train)
X_train_processed = preprocess.transform(X_train)
X_test_processed = preprocess.transform(X_test)
    
mode=st.radio(
       "Choose Detection Model",
       [
              "Single model",
              "Compare all models",
       ]
)

if mode=="Single model":
       model=st.radio(
       "Choose Detection Model",
       [
              "One-Class SVM",
              "Local Outlier Factor",
              "Isolation Forest"
       ]
)
       
       if model=="One-Class SVM":
          st.subheader("One-Class SVM Parameters")
          gamma=st.selectbox( "Gamma",
        [
            "scale",
            "auto",
            0.0001,
            0.001,
            0.01,
            0.1
        ],
        index=5
    )
          nu = st.slider(
          "Nu",
          0.01,
          0.50,
          0.30
    )

       elif model=="Local Outlier Factor":
         st.subheader("Local Outlier Factor Parameters")
         neighbors = st.slider(
        "Neighbors",
         5,
         100,
         40
    )
         contamination=st.slider(
         "Contamination",
         0.01,
         0.50,
         0.50
         )

       elif model=="Isolation Forest":
         st.subheader("Isolation Forest Parameters")
         contamination = st.slider(
         "Contamination",
         0.01,
         0.50,
         0.50
    )

         n_estimators = st.slider(
        "Number of Trees",
         10,
         300,
         50
    )

         max_samples = st.selectbox(
       "Max Samples",
        [256,512,1024,2048],
        index=3
    )
       # st.info("Open the Results page to view the comparison.")

elif mode=="Compare all models":
      st.info("""
The following models will be executed:

✅ Isolation Forest

✅ Local Outlier Factor

✅ One-Class SVM

The optimized parameters identified during experimentation will be used.
""")

st.divider()

if st.button("🚀 Run Detection",use_container_width=True):
    if mode == "Single model":
       if model=="One-Class SVM":
                st.subheader("One-Class SVM ")
                X_train_normal=X_train[y_train==0]
                preprocess.fit(X_train_normal)
                x_train_processed=preprocess.transform(X_train_normal)
                X_test_processed=preprocess.transform(X_test)
                ocs=OneClassSVM(
              kernel="rbf",gamma=gamma,nu=nu
          )
                ocs.fit(x_train_processed)
                pred_binary=ocs.predict(X_test_processed)
                pred_binary=np.where(pred_binary == 1, 0, 1)
       elif model=="Local Outlier Factor":
               st.subheader("Local Outlier Factor Parameters")
               lof=LocalOutlierFactor(
               n_neighbors=neighbors,contamination=contamination,novelty=True
          )
               lof.fit(X_train_processed)
               pred_binary=lof.predict(X_test_processed)
               pred_binary=np.where(pred_binary==-1,1,0)
      
       elif model=="Isolation Forest":
               st.subheader("Isolation Forest Parameters")
               clf = IsolationForest(
              n_estimators=n_estimators,
              max_samples=max_samples,
              contamination=contamination,
              random_state=42
          )
      
               clf.fit(X_train_processed)
      
               predictions = clf.predict(X_test_processed)
               pred_binary = np.where(predictions == -1, 1, 0)

       accuracy = accuracy_score(y_test, pred_binary)
       precision = precision_score(y_test, pred_binary,zero_division=0)
       recall = recall_score(y_test, pred_binary, zero_division=0)
       f1 = f1_score(y_test, pred_binary,zero_division=0)
       cm = confusion_matrix(y_test, pred_binary)
       report = classification_report(
    y_test,
    pred_binary,
    output_dict=True
)
       st.session_state["results"] = {
    "type": "single",

    "model": model,

    "accuracy": accuracy,

    "precision": precision,

    "recall": recall,

    "f1": f1,

    "confusion_matrix": cm,

    "report": report
}
       results = st.session_state["results"]
      
       st.success("✅ Threat detection completed successfully!")
       st.info("Go to the Results page to view detailed metrics.")

    elif mode == "Compare all models":
          comparison = []
          clf = IsolationForest(
                        n_estimators=50,
                        max_samples=2048,
                        contamination=0.5,
                        random_state=42
                    )
                
          clf.fit(X_train_processed)
          pred = clf.predict(X_test_processed)
          pred = np.where(pred == -1, 1, 0)
          acc = accuracy_score(y_test, pred)
          prec = precision_score(y_test, pred, zero_division=0)
          rec = recall_score(y_test, pred, zero_division=0)
          f1 = f1_score(y_test, pred, zero_division=0)
          comparison.append({

    "Model":"Isolation Forest",

    "Accuracy":acc,

    "Precision":prec,

    "Recall":rec,

    "F1":f1
})
          lof=LocalOutlierFactor( n_neighbors=40,contamination=0.5,novelty=True)
          lof.fit(X_train_processed)
          pred_binary=lof.predict(X_test_processed)
          pred_binary=np.where(pred_binary==-1,1,0)
          acc = accuracy_score(y_test, pred_binary)
          prec = precision_score(y_test, pred_binary, zero_division=0)
          rec = recall_score(y_test, pred_binary, zero_division=0)
          f1 = f1_score(y_test, pred_binary, zero_division=0)
          comparison.append({

    "Model":"Local Outlier Factor",

    "Accuracy":acc,

    "Precision":prec,

    "Recall":rec,

    "F1":f1
})
          X_train_normal=X_train[y_train==0]
          preprocess.fit(X_train_normal)
          x_train_processed=preprocess.transform(X_train_normal)
          X_test_processed=preprocess.transform(X_test)
          ocs=OneClassSVM(
                        kernel="rbf",gamma=0.1,nu=0.30
                    )
          ocs.fit(x_train_processed)
          pred_b=ocs.predict(X_test_processed)
          pred_b=np.where(pred_b == 1, 0, 1)
          acc = accuracy_score(y_test, pred_b)
          prec = precision_score(y_test, pred_b, zero_division=0)
          rec = recall_score(y_test, pred_b, zero_division=0)
          f1 = f1_score(y_test, pred_b, zero_division=0)
          comparison.append({
          
              "Model":"One-Class SVM",
          
              "Accuracy":acc,
          
              "Precision":prec,
          
              "Recall":rec,
          
              "F1":f1
          })
          comparison = pd.DataFrame(comparison)
          comparison = comparison.sort_values(
    by="Accuracy",
    ascending=False
)
#           st.session_state["comparison"] = comparison
#           best = comparison.iloc[0]
#           st.session_state["best_model"] = best
#           st.success("✅ All models compared successfully.")
#           st.info("Open the Results page to see the ranking.")
#           if "comparison" in st.session_state:
#                 st.subheader("🏆 Model Comparison")
#                 st.dataframe(
#               st.session_state["comparison"],
#         use_container_width=True
#     )
#     best = st.session_state["best_model"]
          st.session_state["results"] = {
    "type": "comparison",
    "comparison": comparison,
    "best_model": comparison.iloc[0].to_dict()}

          st.success("✅ Model comparison completed successfully!")
          st.info("Open the Results page to view the comparison.")