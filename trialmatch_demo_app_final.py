
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# Load API key securely
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page config and logo
st.set_page_config(page_title="TrialMatch Demo", page_icon="🔬")
st.image("A_logo_for_a_company_named_TrialMatch_is_displayed.png", width=180)
st.title("TrialMatch – התאמת מטופלים למחקרים קליניים באמצעות בינה מלאכותית")

# File upload section
protocol_file = st.file_uploader("📄 העלה את פרוטוקול המחקר (PDF)", type="pdf")
medical_files = st.file_uploader("📁 העלה קבצי מידע רפואי של המטופל (PDF)", type="pdf", accept_multiple_files=True)

if protocol_file and medical_files:
    with st.spinner("🔍 מבצע ניתוח והשוואה..."):
        # Extract text from protocol
        protocol_reader = PdfReader(protocol_file)
        protocol_text = "\n".join([page.extract_text() for page in protocol_reader.pages])

        # Extract inclusion/exclusion criteria using GPT
        criteria_prompt = f'''
        אתה מקבל כקלט טקסט מתוך פרוטוקול של מחקר קליני.
        אנא אתר רק את סעיפי קריטריוני ההכללה ואי-הכללה.
        החזר רק את הטקסט של הקריטריונים בצורה ברורה, כך:

        קריטריוני הכללה:
        - ...
        - ...

        קריטריוני אי-הכללה:
        - ...
        - ...

        טקסט הפרוטוקול:
        {protocol_text[:6000]}
        '''

        extracted_criteria = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": criteria_prompt}]
        ).choices[0].message.content

        # Combine all medical files
        all_medical_text = ""
        for file in medical_files:
            reader = PdfReader(file)
            all_medical_text += "\n".join([page.extract_text() for page in reader.pages])

        # Matching logic
        matching_prompt = f'''
        יש בידך את קריטריוני ההכללה והאי-הכללה למחקר קליני, וכן מידע רפואי של מטופלת.

        עליך להשוות בין שניהם ולכתוב בצורה ברורה:

        - עבור כל קריטריון ציין אם מתקיים או לא, והסבר מדוע.
        - אם חסר מידע – ציין זאת במפורש.
        - בסיום, כתוב פסקה מסכמת ברורה: האם נראה שהמטופלת מתאימה למחקר? אם לא – מה חסר?

        קריטריוני מחקר:
        {extracted_criteria}

        מידע רפואי של המטופלת:
        {all_medical_text[:6000]}
        '''

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": matching_prompt}]
        ).choices[0].message.content

        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)

