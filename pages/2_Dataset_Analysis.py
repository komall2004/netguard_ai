import streamlit as st
import pandas as pd
st.title("📊 Dataset Analysis")
if "df" not in st.session_state:
    st.warning("⚠ Please upload a dataset first.")
    st.stop()
df=st.session_state["df"]

col1,col2,col3,col4=st.columns(4)
with col1:
    st.metric("Rows",df.shape[0])
with col2:
    st.metric("Columns",df.shape[1])
with col3:
    st.metric("Missing Values",df.isnull().sum().sum())
with col4:
    st.metric("Duplicate Rows",df.duplicated().sum())
with st.expander("📄 View Dataset"):
    st.dataframe(df)

# st.subheader("📈 Summary Statistics")
# st.dataframe(df.describe(include="all"),use_container_width=True)

st.subheader("📉 Missing Values")
missing_df=pd.DataFrame({
     "Columns":df.columns,
     "Missing":df.isnull().sum().values,
     "percentage":(df.isnull().sum()/len(df)*100)
})
st.dataframe(missing_df,use_container_width=True)
st.subheader("📋 Column Information")
tab1,tab2,tab3=st.tabs(["📄 Preview", "📊 Dataset Info","📈 Statistics"])
with tab1:
        st.dataframe(df.head(20),use_container_width=True)
with tab2:
        info_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum().values,
        "Unique Values": df.nunique().values
    })
with tab3:
        st.dataframe(df.describe(include="all"),use_container_width=True)
st.dataframe(info_df, use_container_width=True)


