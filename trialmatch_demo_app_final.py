
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import os

# Load API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page config and logo
st.set_page_config(page_title="TrialMatch Demo", page_icon="🔬")
st.image("trialmatch_logo_small.png", width=120)
st.title("TrialMatch – התאמת מטופלים למחקרים קליניים באמצעות בינה מלאכותית")

# Upload files
protocol_file = st.file_uploader("📄 העלה את פרוטוקול המחקר (PDF)", type="pdf")
medical_files = st.file_uploader("📁 העלה קבצי מידע רפואי של המטופל (PDF)", type="pdf", accept_multiple_files=True)

if protocol_file and medical_files:
    with st.spinner("🔍 מבצע ניתוח והשוואה..."):
        # Read protocol PDF
        protocol_reader = PdfReader(protocol_file)
        protocol_text = "\n".join([page.extract_text() for page in protocol_reader.pages])

        # Extract only inclusion/exclusion criteria using GPT
        extraction_prompt = f'''
        להלן טקסט מתוך פרוטוקול מחקר קליני. אתר רק את סעיפי הקריטריונים להכללה ואי-הכללה.
        החזר את הטקסט שלהם בלבד בפורמט ברור:
        ### קריטריוני הכללה:
        ...
        ### קריטריוני אי-הכללה:
        ...
        
        פרוטוקול:
        {protocol_text[:6000]}
        '''

        extracted_criteria = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": extraction_prompt}]
        ).choices[0].message.content

        # Read medical PDFs
        all_medical_text = ""
        for file in medical_files:
            reader = PdfReader(file)
            all_medical_text += "\n".join([page.extract_text() for page in reader.pages])

        # Perform smart matching using GPT
        matching_prompt = f'''
        נתח את ההתאמה בין מידע רפואי של מטופל לבין קריטריוני מחקר קליני.

        קריטריוני מחקר:
        {extracted_criteria}

        מידע רפואי של המטופל:
        {all_medical_text[:6000]}

        החזר תשובה בפורמט:
        • קריטריונים שנבדקו – לכל אחד ציין האם מתקיים או לא, והסבר קצר
        • אם חסר מידע – כתוב זאת
        • מסקנה סופית – האם המטופל מתאים למחקר? והאם נדרשת בדיקה נוספת.

        נא להציג זאת באופן מסודר וברור.
        '''

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": matching_prompt}]
        ).choices[0].message.content

        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)
