import streamlit as st
from PIL import Image
import pandas as pd
from ocr_utils import ocr_image
import pytesseract
import shutil
import os
from parser import parse_holdings
import plotly.express as px

st.set_page_config(layout='wide', page_title='Holdings Analyzer')

st.title('Holdings Analyzer — Prototype')

# Tesseract detection + override in sidebar
def _detect_tesseract_path():
    cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
    if cmd and os.path.exists(cmd):
        return cmd
    path = shutil.which('tesseract')
    return path

detected_path = _detect_tesseract_path()
st.sidebar.header('Tesseract OCR')
if detected_path:
    st.sidebar.success('Detected: ' + detected_path)
else:
    st.sidebar.warning('Tesseract not found')

custom_path = st.sidebar.text_input('Tesseract path override', value=detected_path or '')
if st.sidebar.button('Set Tesseract path'):
    if custom_path:
        pytesseract.pytesseract.tesseract_cmd = custom_path
        st.sidebar.success('Path set; please re-run OCR upload.')
    else:
        st.sidebar.error('Provide a valid path before setting.')

st.markdown('Upload a screenshot of your holdings statement; the app will attempt to extract holdings and show a simple dashboard.')

uploaded = st.file_uploader('Upload screenshot', type=['png','jpg','jpeg'])

# OCR options
st.sidebar.header('OCR options')
psm = st.sidebar.selectbox('Tesseract PSM (page segmentation mode)', options=['3','6','11'], index=1)
preprocess_opt = st.sidebar.checkbox('Run preprocessing (deskew, denoise)', value=True)
show_pre = st.sidebar.checkbox('Show preprocessed image', value=False)

if uploaded is not None:
    image = Image.open(uploaded).convert('RGB')
    st.image(image, caption='Uploaded screenshot', use_column_width=True)

    with st.spinner('Running OCR...'):
        try:
            if show_pre:
                text, pre_img = ocr_image(image, psm=int(psm), preprocess=preprocess_opt, return_image=True)
            else:
                text = ocr_image(image, psm=int(psm), preprocess=preprocess_opt)
        except pytesseract.TesseractNotFoundError:
            st.error('Tesseract OCR not found on this machine.')
            st.markdown('''
Install Tesseract and ensure it's on your PATH, or set the path in code:

- Chocolatey (Windows, run PowerShell as Admin):

```powershell
choco install tesseract -y
```

- Or download installer from the releases page: https://github.com/tesseract-ocr/tesseract/releases

After installing, restart your terminal and re-run the app. Alternatively set the path in Python:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```
''')
            st.stop()
        except pytesseract.TesseractError as e:
            st.error('Tesseract failed to initialize: ' + str(e))
            st.markdown('''
Common fixes:

- Make sure the `tessdata` folder exists next to your `tesseract.exe` and contains language files like `eng.traineddata`.
- Set `TESSDATA_PREFIX` to the parent directory of `tessdata` (example below).

PowerShell (session only):
```powershell
$env:TESSDATA_PREFIX = 'C:\\Program Files\\Tesseract-OCR'
```

PowerShell (permanent):
```powershell
setx TESSDATA_PREFIX "C:\\Program Files\\Tesseract-OCR"
```

Or set in Python before OCR:
```python
import os
os.environ['TESSDATA_PREFIX'] = r"C:\\Program Files\\Tesseract-OCR"
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
''')
            st.stop()

    st.subheader('OCR text (preview)')
    st.text_area('OCR', value=text, height=200)

    if show_pre:
        st.subheader('Preprocessed image')
        st.image(pre_img, use_column_width=True)

    st.subheader('Parsed holdings (heuristic)')
    df = parse_holdings(text)

    if df.empty:
        st.warning('No structured holdings found. Try a clearer screenshot or crop to the holdings table.')
    else:
        st.dataframe(df)

        # Basic analysis
        total_value = df['value'].sum()
        if total_value == 0:
            st.info('Values not extracted; showing quantities only.')
        else:
            df['pct'] = df['value'] / total_value * 100
            fig = px.pie(df, names='symbol', values='value', title='Portfolio allocation')
            st.plotly_chart(fig, use_container_width=True)

            # Simple suggestions
            st.subheader('Suggestions')
            overweight = df[df['pct'] > 50]
            if not overweight.empty:
                st.markdown('- **Diversify:** large allocation in ' + ', '.join(overweight['symbol'].tolist()))
            else:
                st.markdown('- Allocation looks reasonably diversified (no single holding >50%)')

else:
    st.info('Upload a screenshot to begin.')
