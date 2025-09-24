import streamlit as st
import pandas as pd
from io import BytesIO

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
        unmatched_df = df1[~df1["A"].isin(personnr_list)].copy()
        if not unmatched_df.empty:
            # Copy from the preceding unnamed column (index 1) into Differens
            try:
                # Get second column name (the placeholder pd.NA may appear as None or NaN)
                second_col_name = unmatched_df.columns[1]
                raw_series = unmatched_df[second_col_name].astype(str)
                # Remove surrounding parentheses and internal parentheses while keeping minus signs
                cleaned = raw_series.str.replace(r'[()]', '', regex=True).str.strip()
                # Optionally convert comma decimal to dot
                cleaned = cleaned.str.replace(',', '.', regex=False)
                unmatched_df['Differens'] = cleaned
            except Exception:
                pass

        # st.subheader("Matched Rows from Underlag")
        # st.dataframe(matched_df)

        
        st.subheader("Unmatched Rows from Underlag")
        st.dataframe(unmatched_df)

        if not unmatched_df.empty:
            # Prepare XLSX in-memory
            xlsx_buffer = BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
                unmatched_df.to_excel(writer, index=False, sheet_name="Unmatched")
            xlsx_buffer.seek(0)
            st.download_button(
                label="Download Unmatched Rows as XLSX",
                data=xlsx_buffer,
                file_name='unmatched_rows.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )

    
        if justeringsar:
            # Filter for positive 'Summa Ny-beräkning'
            positive_matched_df = matched_df[pd.to_numeric(matched_df['Summa Ny-beräkning'], errors='coerce') > 0].copy()

            if not positive_matched_df.empty:
                # Ensure Belopp is numeric based on Differens column if present
                belopp_series = pd.to_numeric(positive_matched_df.get("Differens", pd.Series(dtype=str)), errors='coerce')
                justeringstyp_series = belopp_series.apply(lambda v: "Manuell faktura" if pd.notna(v) and v < 0 else "Makulering")
                new_df = pd.DataFrame({
                    "Justeringstyp": justeringstyp_series,
                    "Justeringsår": justeringsar,
                    "Justeringsmånad": "",
                    "Personnummer": positive_matched_df["A"],
                    "Belopp": belopp_series,
                    "Beskrivning": "Kommer från Extens"
                })

                st.subheader("Justeringsunderlag")
                st.dataframe(new_df)

                st.download_button(
                    label="Download Justeringsunderlag as CSV",
                    data=new_df.to_csv(index=False, sep=';').encode('ISO‑8859‑1'),
                    file_name='justeringsunderlag.csv',
                    mime='text/csv',
                )

    except Exception as e:
        st.error(f"Error processing files: {e}")
