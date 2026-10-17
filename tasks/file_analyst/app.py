"""Independent File Analyst task UI. Edit this file to change only this task."""
from core.services import *

TASK_NAME = "File Analyst"
TASK_ICON = "📊"


def render():
    page = "File Analyst"
    if page == 'File Analyst':
        st.subheader('File Analyst')
        st.write('Upload a CSV or Excel workbook. Files are processed by this app and are not automatically sent to an external AI service.')
        uploaded = st.file_uploader('Choose a file', type=['csv', 'xlsx', 'xls'])
        if uploaded:
            try:
                if uploaded.name.lower().endswith('.csv'): df = pd.read_csv(uploaded)
                else:
                    workbook = pd.ExcelFile(uploaded)
                    selected_sheet = st.selectbox('Select worksheet', workbook.sheet_names)
                    df = pd.read_excel(workbook, sheet_name=selected_sheet)
                st.success('File loaded successfully.')
                m1, m2, m3 = st.columns(3)
                m1.metric('Rows', f'{len(df):,}'); m2.metric('Columns', f'{len(df.columns):,}'); m3.metric('Missing cells', f'{int(df.isna().sum().sum()):,}')
                st.dataframe(df.head(100), use_container_width=True)
                with st.expander('Summary and data quality'): st.text(dataframe_summary(df))
                numeric_columns = df.select_dtypes(include='number').columns.tolist()
                if numeric_columns:
                    selected_numeric = st.selectbox('Numeric column to analyze', numeric_columns)
                    values = pd.to_numeric(df[selected_numeric], errors='coerce').dropna()
                    if not values.empty:
                        a, b, c, d = st.columns(4)
                        a.metric('Average', f'{values.mean():,.4f}'); b.metric('Median', f'{values.median():,.4f}'); c.metric('Minimum', f'{values.min():,.4f}'); d.metric('Maximum', f'{values.max():,.4f}')
                st.download_button('Download current sheet as CSV', df.to_csv(index=False).encode('utf-8'), file_name='analyzed_data.csv', mime='text/csv')
            except Exception as exc: st.error(f'Could not read this file: {exc}')
