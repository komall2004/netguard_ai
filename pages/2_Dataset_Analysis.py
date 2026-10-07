# import streamlit as st
# import pandas as pd
# st.title("📊 Dataset Analysis")
# if "df" not in st.session_state:
#     st.warning("⚠ Please upload a dataset first.")
#     st.stop()
# df=st.session_state["df"]

# col1,col2,col3,col4=st.columns(4)
# with col1:
#     st.metric("Rows",df.shape[0])
# with col2:
#     st.metric("Columns",df.shape[1])
# with col3:
#     st.metric("Missing Values",df.isnull().sum().sum())
# with col4:
#     st.metric("Duplicate Rows",df.duplicated().sum())
# with st.expander("📄 View Dataset"):
#     st.dataframe(df)

# # st.subheader("📈 Summary Statistics")
# # st.dataframe(df.describe(include="all"),use_container_width=True)

# st.subheader("📉 Missing Values")
# missing_df=pd.DataFrame({
#      "Columns":df.columns,
#      "Missing":df.isnull().sum().values,
#      "percentage":(df.isnull().sum()/len(df)*100)
# })
# st.dataframe(missing_df,use_container_width=True)
# st.subheader("📋 Column Information")
# tab1,tab2,tab3=st.tabs(["📄 Preview", "📊 Dataset Info","📈 Statistics"])
# with tab1:
#         st.dataframe(df.head(20),use_container_width=True)
# with tab2:
#         info_df = pd.DataFrame({
#         "Column": df.columns,
#         "Data Type": df.dtypes.astype(str),
#         "Missing Values": df.isnull().sum().values,
#         "Unique Values": df.nunique().values
#     })
# with tab3:
#         st.dataframe(df.describe(include="all"),use_container_width=True)
# st.dataframe(info_df, use_container_width=True)

import streamlit as st
import pandas as pd
from frontend_api import send_to_backend


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dataset Analysis",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CHECK DATASET
# ============================================================

if "df" not in st.session_state:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()


df = st.session_state["df"].copy()
# st.write("### DEBUG - Analysis Page")
# st.write("Filename:", st.session_state.get("filename"))
# st.write("Shape:", df.shape)
# st.write(
#     "Missing values:",
#     df.isnull().sum().sum()
# )

# ============================================================
# CALL FASTAPI
# ============================================================

response = send_to_backend(
    "/analyze",
    df
)


if response.status_code == 200:

    result = response.json()

else:

    st.error(
        f"FastAPI error: {response.status_code}"
    )

    st.write(response.text)

    st.stop()


# ============================================================
# TITLE
# ============================================================

st.title("📊 Dataset Analysis")


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Rows",
        result["rows"]
    )


with col2:
    st.metric(
        "Columns",
        result["columns"]
    )


with col3:

    missing_values = result.get(
        "missing_values",
        {}
    )

    missing_total = sum(
        missing_values.values()
    )

    st.metric(
        "Missing Values",
        missing_total
    )


with col4:

    st.metric(
        "Duplicate Rows",
        result["duplicate_rows"]
    )


# ============================================================
# DATASET PREVIEW
# ============================================================

with st.expander("📄 View Dataset"):

    st.dataframe(
        df,
        use_container_width=True
    )


# ============================================================
# MISSING VALUES
# ============================================================

st.subheader("📉 Missing Values")


missing_values = result.get(
    "missing_values",
    {}
)

missing_percentage = result.get(
    "missing_percentage",
    {}
)


# Only show columns that actually contain missing values

missing_cols = {
    col: count
    for col, count in missing_values.items()
    if count > 0
}


if len(missing_cols) == 0:

    st.success(
        "✅ No missing values detected."
    )

else:

    missing_df = pd.DataFrame({

        "Column": list(
            missing_cols.keys()
        ),

        "Missing": list(
            missing_cols.values()
        ),

        "Percentage": [
            missing_percentage.get(
                col,
                0
            )
            for col in missing_cols
        ]

    })

    st.dataframe(
        missing_df,
        use_container_width=True
    )


# ============================================================
# COLUMN INFORMATION
# ============================================================

st.subheader("📋 Column Information")


tab1, tab2, tab3 = st.tabs(
    [
        "📄 Preview",
        "📊 Dataset Info",
        "📈 Statistics"
    ]
)


# ============================================================
# PREVIEW
# ============================================================

with tab1:

    st.dataframe(
        df.head(20),
        use_container_width=True
    )


# ============================================================
# DATASET INFO
# ============================================================

with tab2:

    info_df = pd.DataFrame({

        "Column": df.columns,

        "Data Type": [
            result["data_types"].get(
                str(col),
                str(df[col].dtype)
            )
            for col in df.columns
        ],

        "Missing Values": [
            missing_values.get(
                str(col),
                0
            )
            for col in df.columns
        ],

        "Unique Values": [
            df[col].nunique()
            for col in df.columns
        ]

    })

    st.dataframe(
        info_df,
        use_container_width=True
    )


# ============================================================
# STATISTICS
# ============================================================

with tab3:

    st.dataframe(
        df.describe(
            include="all"
        ),
        use_container_width=True
    )
