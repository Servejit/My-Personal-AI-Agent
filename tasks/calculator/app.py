"""Independent Calculator task UI. Edit this file to change only this task."""
from core.services import *


def render():
    page = "Calculator"
    elif page == 'Calculator':
        st.subheader('Safe Calculator')
        st.write('Supports numbers, parentheses, +, -, *, /, //, %, and **. Arbitrary Python code is not executed.')
        expression = st.text_input('Expression', placeholder='(125 * 8) / 4')
        if st.button('Calculate', type='primary'):
            try:
                result = safe_calculate(expression)
                st.success(f'Result: {result:,}' if isinstance(result, int) else f'Result: {result}')
            except Exception as exc: st.error(str(exc))
