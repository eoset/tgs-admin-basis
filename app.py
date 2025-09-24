import streamlit as st
import pandas as pd

st.title("XLSX File Uploader and Viewer")

underlag_columns = [
    "A",
    pd.NA,
    "Differens",
    "Summa fakturerat",
    "Summa Ny-beräkning",
    "Justering",
    "Årsinkomst/12",
    "Debiteringsavvikelse"
]

berakningsgrundare_columns = [
    "Beräkningsgrundare personnr",
    "Differens",
    "Summa fakturerat",
    "Summa ny beräkning",
    "Manuella justeringar",
    "Tillägg/Avdrag"
]

st.header("Upload Underlag till Justeringar File")
underlag_file = st.file_uploader("Choose a .xlsx file", type="xlsx", key="1")

st.header("Upload Beräkningsgrundare File")
berakningsgrundare_file = st.file_uploader("Choose a .xlsx file", type="xlsx", key="2")


df1 = None
df2 = None

if underlag_file is not None:
    try:
        df1 = pd.read_excel(underlag_file, names=underlag_columns, header=0)
        # st.subheader("Underlag till Justeringar")
        # st.dataframe(df1)
    except Exception as e:
        st.error(f"Error reading the first file: {e}")

if berakningsgrundare_file is not None:
    try:
        df2 = pd.read_excel(berakningsgrundare_file, names=berakningsgrundare_columns, header=0)
        # st.subheader("Beräkningsgrundare")
        # st.dataframe(df2)
    except Exception as e:
        st.error(f"Error reading the second file: {e}")

justeringsar = st.text_input("Ange Justeringsår")

if df1 is not None and df2 is not None:
    try:
        personnr_list = df2["Beräkningsgrundare personnr"].tolist()
        matched_df = df1[df1["A"].isin(personnr_list)]
        unmatched_df = df1[~df1["A"].isin(personnr_list)]

        # st.subheader("Matched Rows from Underlag")
        # st.dataframe(matched_df)

        
        st.subheader("Unmatched Rows from Underlag")
        st.dataframe(unmatched_df)

        if not unmatched_df.empty:
            st.download_button(
                label="Download Unmatched Rows as CSV",
                data=unmatched_df.to_csv(index=False).encode('utf-8'),
                file_name='unmatched_rows.csv',
                mime='text/csv',
            )

    
        if justeringsar:
            # Filter for positive 'Summa Ny-beräkning'
            positive_matched_df = matched_df[pd.to_numeric(matched_df['Summa Ny-beräkning'], errors='coerce') > 0].copy()

            if not positive_matched_df.empty:
                new_df = pd.DataFrame({
                    "Justeringstyp": "Makulering",
                    "Justeringsår": justeringsar,
                    "Justeringsmånad": "",
                    "Personnummer": positive_matched_df["A"],
                    "Belopp": positive_matched_df["Summa Ny-beräkning"]
                })

                st.subheader("Justeringsunderlag")
                st.dataframe(new_df)

                st.download_button(
                    label="Download Justeringsunderlag as CSV",
                    data=new_df.to_csv(index=False).encode('utf-8'),
                    file_name='justeringsunderlag.csv',
                    mime='text/csv',
                )

    except Exception as e:
        st.error(f"Error processing files: {e}")
