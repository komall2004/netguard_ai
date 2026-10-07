import streamlit as st
import pandas as pd
import numpy as np

from sklearn.preprocessing import (
    LabelEncoder,
    OrdinalEncoder,
    MinMaxScaler,
    StandardScaler,
    RobustScaler
)

from frontend_api import send_to_backend


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Data Preprocessing",
    page_icon="🧹",
    layout="wide"
)


# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()


# ============================================================
# CURRENT DATASET
# ============================================================

df = st.session_state["df"].copy()


# ============================================================
# INITIALIZE CLEANED DATASET
# ============================================================

if "cleaned_df" not in st.session_state:
    st.session_state["cleaned_df"] = df.copy()


cleaned_df = st.session_state["cleaned_df"].copy()


# ============================================================
# FASTAPI RECOMMENDATIONS
# ============================================================

response = send_to_backend(
    "/preprocessing-recommendations",
    df
)


if response.status_code == 200:

    preprocessing_result = response.json()

else:

    st.error(
        f"FastAPI error: {response.status_code}"
    )

    st.write(response.text)

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title("🧹 Data Preprocessing")
if "df" not in st.session_state:
    st.warning("Upload Dataset First")
    st.stop()

def recommend(df,col):
   missing_percentage=df[col].isnull().mean()*100
   if missing_percentage>40:
      return "Drop Columns"
   if pd.api.types.is_numeric_dtype(df[col]):
      q1,q3=np.percentile(df[col],[25,75])
      iqr = q3 -q1
      lower = q1 - 1.5 * iqr
      upper = q3 + 1.5 * iqr
      outliers=((df[col]<q1-1.5*iqr)|(df[col]>q1+1.5*iqr)).sum()
      if outliers>0:
         return "Median"   
      return "Mean"
   return "Mode"

df=st.session_state["df"].copy()

col1,col2,col3=st.columns(3)
with col1:
    st.metric("Rows",df.shape[0])
with col2:
    st.metric("Columns",df.shape[1])
with col3:
    st.metric("Missing",df.isnull().sum().sum())
# Fix header row if column names are numeric
if all(isinstance(col, int) for col in cleaned_df.columns):

    cleaned_df.columns = cleaned_df.iloc[0].astype(str)

    cleaned_df = cleaned_df.iloc[1:].reset_index(drop=True)

    st.session_state["cleaned_df"] = cleaned_df.copy()

with st.expander("🗑 Column Removal"):

    columns = cleaned_df.columns.tolist()

    selected_columns = st.multiselect(
        "Select columns you want to remove",
        columns
    )

    if selected_columns:

        st.warning(
            f"⚠️ You selected {len(selected_columns)} "
            "column(s) for removal."
        )

        if st.button(
            "Remove Selected Columns",
            key="remove_columns"
        ):

            cleaned_df = cleaned_df.drop(
                columns=selected_columns
            )

            st.session_state["cleaned_df"] = (
                cleaned_df.copy()
            )

            st.success(
                "✅ Selected columns removed successfully!"
            )

            st.subheader(
                "✨ Updated Dataset Preview"
            )

            st.dataframe(
                cleaned_df.head(),
                use_container_width=True
            )

with st.expander("🧹 Missing Value Handling"):
  missing_table=pd.DataFrame({"Column":df.columns[df.isnull().sum()>0],
                              "Missing Values":df.isnull().sum()[df.isnull().sum()>0].values})
  st.write("Columns with missing values")
  st.dataframe(missing_table,use_container_width=True)

  missing_cols=df.columns[df.isnull().sum()>0]

#   for col in df.columns:
    #  converted=pd.to_numeric(df[col],errors="coerce")
    #  if converted.notna().sum() > 0.8 * len(df):
    #     df[col] = converted
    #  st.session_state["cleaned_df"]=df.copy()
  cleaned_df=st.session_state["cleaned_df"].copy()  


  selected_method={}
  for col in missing_cols:
    recommendations=recommend(df,col)
    st.write(f"{col}  {df[col].dtype}")
    st.write(f"Recommendation {recommendations}")
    selected_method[col]=st.selectbox(
      "Choose Method",
      ["Mean","Median","Mode","Drop Rows","Drop Columns"],
      index=["Mean","Median","Mode","Drop Rows","Drop Columns"].index(recommendations),
      key=col
)
    st.divider()
    
  if st.button("Apply"):
    #  if "cleaned_df" not in st.session_state:
    #     st.session_state["cleaned_df"]=df.copy()

    #  cleaned_df = st.session_state["cleaned_df"]

     numeric=df.select_dtypes(exclude="object").columns
     categorical=df.select_dtypes(include="object").columns

     for col,method in selected_method.items():
       if method=="Mean":
        cleaned_df[col]=cleaned_df[col].fillna(cleaned_df[col].mean())
        cleaned_df[col]=cleaned_df[col].fillna(cleaned_df[col].mode().iloc[0])

       elif method=="Median":
        cleaned_df[col]=cleaned_df[col].fillna(cleaned_df[col].median())
        cleaned_df[col]=cleaned_df[col].fillna(cleaned_df[col].mode().iloc[0])

       elif method=="Mode":
        for col in cleaned_df:
          cleaned_df[col]=cleaned_df[col].fillna(cleaned_df[col].mode().iloc[0])

       elif method=="Drop Rows":
            cleaned_df=cleaned_df.dropna()

       elif method == "Drop Columns":
            cleaned_df = cleaned_df.drop(columns=[col])
        
     st.session_state["cleaned_df"]=cleaned_df
     st.dataframe(cleaned_df.head(), use_container_width=True)

     before=df.isnull().sum().sum()
     after=cleaned_df.isnull().sum().sum()

     col1,col2=st.columns(2)
     with col1:
        st.metric("Before",before)
     with col2:
        st.metric("After",after)

     st.subheader("✨ Cleaned Dataset Preview")
     st.dataframe(cleaned_df.head(),use_container_width=True)


with st.expander("🗑 Duplicate Handling"):
  duplicates=df.duplicated().sum()
  st.metric("Duplicat rows",duplicates)
  if st.button("Remove duplicates"):
     before=len(cleaned_df)
     cleaned_df=cleaned_df.drop_duplicates()
     after=len(cleaned_df)
     st.session_state["cleaned_df"]=cleaned_df
     st.success("Duplicates removed")


with st.expander("🏷 Encoding"):
  categorical=cleaned_df.select_dtypes(include="object").columns
  st.dataframe(
    pd.DataFrame(
        {"Categorical Columns":categorical}
    ),
    use_container_width=True
)
  if len(categorical)>0:
     st.info(
        """
🧠 Recommendation

**One Hot Encoding**

Reason:
The detected categorical columns appear to be nominal rather than ordinal, so One Hot Encoding is recommended.
"""
    )
 
  method_cat=st.selectbox(
    "Choose Method",
    ["Label Encoding","One hot Encoding","Ordinal Encoding","No Encoding"]
)
  if st.button("Apply encoding", key="apply_encoding"):

    if method_cat == "Label Encoding":

        encoder = LabelEncoder()

        for col in categorical:
            cleaned_df[col] = encoder.fit_transform(
                cleaned_df[col].astype(str)
            )

    elif method_cat == "Ordinal Encoding":

        encoder = OrdinalEncoder()

        cleaned_df[categorical] = encoder.fit_transform(
            cleaned_df[categorical].astype(str)
        )

    elif method_cat == "No Encoding":

        st.info("Encoding skipped.")

    elif method_cat == "One hot Encoding":

        cleaned_df = pd.get_dummies(
            cleaned_df,
            columns=categorical
        )

    # Save updated dataframe
    st.session_state["cleaned_df"] = cleaned_df.copy()

    st.success(
        f"✅ {method_cat} applied successfully!"
    )

    st.subheader("✨ Encoded Dataset Preview")

    st.dataframe(
        cleaned_df.head(),
        use_container_width=True
    )

with st.expander("📏 Scaling"):
  numeric=df.select_dtypes(exclude="object").columns
  outliers=False
  for col in numeric:
     q1,q3=np.percentile(cleaned_df[col],[25,75])
     iqr=q3-q1
     if(
        ((cleaned_df[col] < q1 - 1.5*iqr) |
         (cleaned_df[col] > q3 + 1.5*iqr))
        .sum() > 0
    ):
        outliers=True
        break

  if outliers:
         st.success(
        """
🧠 Recommendation

RobustScaler

Reason:
Outliers were detected in the numerical features.
"""
    )

  else:

    st.success(
        """
🧠 Recommendation

StandardScaler

Reason:
No significant outliers were detected.
"""
    )
     
  st.dataframe(
      pd.DataFrame(
          {"Numerical Columns":numeric}
      ),   use_container_width=True
      )
 
  method_sca=st.selectbox(
    "Choose Method",
    ["StandardScaler","RobustScaler","MinMaxScaler","No Scaling"]
)
  if st.button("Apply scaling", key="apply_scaling"):

    if method_sca == "StandardScaler":

        scaler = StandardScaler()

    elif method_sca == "MinMaxScaler":

        scaler = MinMaxScaler()

    elif method_sca == "RobustScaler":

        scaler = RobustScaler()

    else:

        scaler = None


    if scaler is not None:

        # Get numerical columns from the CURRENT cleaned dataset
        numeric = cleaned_df.select_dtypes(
    include=np.number
).columns.tolist()

        if len(numeric) > 0:

            cleaned_df[numeric] = scaler.fit_transform(
                cleaned_df[numeric]
            )

            st.session_state["cleaned_df"] = (
                cleaned_df.copy()
            )

            st.success(
                f"✅ {method_sca} applied successfully!"
            )

            st.subheader(
                "✨ Scaled Dataset Preview"
            )

            st.dataframe(
                cleaned_df.head(),
                use_container_width=True
            )

        else:

            st.warning(
                "⚠️ No numerical columns available for scaling."
            )

    else:

        st.info(
            "Scaling skipped."
        )

    if scaler is not None:
       cleaned_df[numeric]=scaler.fit_transform(cleaned_df[numeric])
    st.session_state["cleaned_df"]=cleaned_df
    st.success(f"{method_sca} selected")
