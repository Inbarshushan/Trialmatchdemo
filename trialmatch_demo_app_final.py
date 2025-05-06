
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import os

# Load API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page config and logo
st.set_page_config(page_title="TrialMatch Demo", page_icon="🔬")
st.image("A_logo_for_a_company_named_TrialMatch_is_displayed.png", width=180)
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

        # Perform smart matching using GPT with better instruction
        system_prompt = '''
אתה עוזר מחקר קליני במערכת בשם TrialMatch. תפקידך לבדוק האם מטופלת מתאימה להשתתפות במחקר קליני, על סמך השוואה בין המידע הרפואי שלה לבין הקריטריונים מתוך פרוטוקול המחקר.

אנא החזר את תשובתך בפורמט הבא:

1. קריטריוני הכללה (Inclusion Criteria): עבור כל קריטריון – ציין אם מתקיים או לא, עם הסבר קצר.
2. קריטריוני אי-הכללה (Exclusion Criteria): כנ"ל – לכל סעיף הסבר אם מתקיים או לא.
3. מסקנה סופית – האם המטופלת מתאימה למחקר? אם חסר מידע – ציין זאת.

השב בצורה קלינית, מסודרת, בהירה – בשפה מקצועית ונגישה. אל תשתמש במשפטים כלליים. אל תדגיש נושאים משפטיים או סודיות – רק ניתוח קליני של ההתאמה.
'''

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'''
קריטריוני מחקר:
{extracted_criteria}

מידע רפואי של המטופל:
{all_medical_text[:6000]}
                '''}
            ]
        ).choices[0].message.content

        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)
      
