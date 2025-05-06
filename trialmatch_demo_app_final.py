
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

        # Matching prompt
        matching_prompt = f"""
אתה מקבל מידע רפואי של מטופל, לצד קריטריוני הכללה ואי-הכללה ממחקר קליני.

1. השווה את המידע הרפואי של המטופל מול הקריטריונים.
2. הסבר בצורה מקצועית וברורה אם הקריטריון מתקיים או לא, והצג נימוק קליני קצר.
3. כתוב בפורמט הבא:

### קריטריוני הכללה:
1. [שם הקריטריון]
- נדרש: [מה נכתב בפרוטוקול]
- נמצא בתיק המטופל: [מה מופיע במסמך הרפואי]
- הערכה: מתאים / לא מתאים / חסר מידע
- נימוק: [הסבר מקצועי תמציתי]

[חזור על כל הקריטריונים]

### קריטריוני אי-הכללה:
[באותו פורמט, עם אותם סעיפים]

### מסקנה:
- האם המטופל מתאים להשתתף במחקר?
- אם לא, פרט מדוע.
- אם חסר מידע, פרט מה חסר.

קריטריוני מחקר:
{extracted_criteria}

מידע רפואי של המטופל:
{all_medical_text[:6000]}
        """

        # Run the comparison
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": matching_prompt}]
        ).choices[0].message.content

        # Display result
        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)
