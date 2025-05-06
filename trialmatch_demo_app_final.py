
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# Load API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page settings and logo
st.set_page_config(page_title="TrialMatch Demo", page_icon="🔬")
st.image("A_logo_for_a_company_named_TrialMatch_is_displayed.png", width=200)
st.title("TrialMatch – התאמת מטופלים למחקרים קליניים באמצעות בינה מלאכותית")

# File upload section
protocol_file = st.file_uploader("📄 העלה את פרוטוקול המחקר (PDF)", type="pdf")
medical_files = st.file_uploader("📁 העלה קבצי מידע רפואי של המטופל (PDF)", type="pdf", accept_multiple_files=True)

if protocol_file and medical_files:
    with st.spinner("🔍 מבצע ניתוח והשוואה..."):
        # Read protocol PDF
        protocol_reader = PdfReader(protocol_file)
        protocol_text = "\n".join([page.extract_text() for page in protocol_reader.pages])

        # Extract inclusion/exclusion criteria using GPT
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

        # Read and combine all medical PDFs
        all_medical_text = ""
        for file in medical_files:
            reader = PdfReader(file)
            all_medical_text += "\n".join([page.extract_text() for page in reader.pages])

     matching_prompt = f'''
להלן מידע רפואי של מטופלת וקריטריוני הכללה ואי הכללה מתוך פרוטוקול מחקר קליני.
אנא בצע ניתוח מקצועי ומובנה האם המטופלת מתאימה להשתתף במחקר. 
השתמש בפורמט הבא:

### קריטריוני הכללה:
- [ציין כל קריטריון מרכזי, תכתוב האם מתקיים או לא ולמה. תשתמש ב־✅ / ❌ / ⚠️]

### קריטריוני אי-הכללה:
- [בדוק אם קיים מידע על כל קריטריון, וכתוב אותו באותו אופן]

### סיכום:
- סכם בקצרה האם המטופלת מתאימה למחקר.
- אם חסר מידע, ציין בדיוק מה חסר.

שמור על שפה מקצועית, רפואית, ברורה ומובנת – כמו שמסבירים לרופא.
'''

קריטריוני מחקר:
{extracted_criteria}

מידע רפואי של המטופל:
{all_medical_text[:6000]}
        """

        # Run the comparison
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": matching_prompt}]
        ).choices[0].message.content

        # Display result
        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)
