
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import os

# Load API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page config and logo
st.set_page_config(page_title="TrialMatch Demo", page_icon="🔬")
st.image("A_logo_for_a_company_named_TrialMatch_is_displayed.png", width=200)
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
matching_prompt = f'''
אנא נתח את ההתאמה בין מידע רפואי של מטופל לבין קריטריוני מחקר קליני.

החזר את הפלט בפורמט הבא:

### קריטריונים מרכזיים מהפרוטוקול והאם המטופלת עומדת בהם:

#### אבחנה:
- **דרוש**: [מה הקריטריון דורש]
- **המטופלת**: [מה מופיע בתיק הרפואי]
- ✅/❌/⚠️ [התאמה + הסבר קצר]

#### שלב מחלה:
- **דרוש**: [...]
- **המטופלת**: [...]
- ✅/❌/⚠️ [...]

[המשך לכל קריטריון משמעותי: טיפול קודם, טיפול נוכחי, בדיקות וכו']

### ❌ קריטריוני אי-הכללה:
- [לציין אם נמצא משהו רלוונטי לפי המידע הרפואי – אם אין, לציין "לא נמצאו גורמי הוצאה ידועים"]

### מסקנה:
- סכם האם המטופלת מתאימה להשתתף במחקר.
- אם חסר מידע – ציין מה בדיוק חסר, ומה נדרש לבדוק כדי להשלים את התמונה.
"""
קריטריוני מחקר:
{extracted_criteria}

מידע רפואי של המטופל:
{all_medical_text[:6000]}
'''

        ).choices[0].message.content

        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)
      
