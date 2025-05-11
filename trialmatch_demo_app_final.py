
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# Load API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Page settings and logo
st.set_page_config(page_title="TrialMatch Demo", page_icon="🔬")
st.image("A_logo_for_a_company_named_TrialMatch_is_displayed.png", width=200)
st.title("TrialMatch – התאמת מטופלים למחקרים קליניים באמצעות בינה מלאכותית")

# Upload section
protocol_file = st.file_uploader("📄 העלה את פרוטוקול המחקר (PDF)", type="pdf")
medical_files = st.file_uploader("📁 העלה קבצי מידע רפואי של המטופל (PDF)", type="pdf", accept_multiple_files=True)

if protocol_file and medical_files:
    with st.spinner("🔍 מבצע ניתוח והשוואה..."):
        # Read protocol
        protocol_reader = PdfReader(protocol_file)
        protocol_text = "\n".join([page.extract_text() for page in protocol_reader.pages])

        # Step 1: Extract criteria
        extraction_prompt = f"""
        להלן טקסט מתוך פרוטוקול מחקר קליני. אתר רק את סעיפי הקריטריונים להכללה ואי-הכללה.
        החזר את הטקסט שלהם בלבד בפורמט ברור:
        ### קריטריוני הכללה:
        ...
        ### קריטריוני אי-הכללה:
        ...
        
        פרוטוקול:
        {protocol_text[:6000]}
        """

        extracted_criteria = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": extraction_prompt}]
        ).choices[0].message.content

        # Step 2: Read all medical PDFs
        all_medical_text = ""
        for file in medical_files:
            reader = PdfReader(file)
            all_medical_text += "\n".join([page.extract_text() for page in reader.pages])

        # Step 3: Smart matching with example
        matching_prompt = f"""
להלן דוגמה לתשובה מסודרת:

אבחנה:
דרוש: סרטן שד מוקדם (Early Breast Cancer), חיובי ל-ER, שלילי ל-HER2.
המטופלת: HR+ (ER חיובי), HER2−.
✔️ מתאים.

שלב מחלה:
דרוש: שלב I-III בסיכון בינוני או גבוה (טבלה 4 בפרוטוקול).
המטופלת: שלב מוקדם, ללא עדות למחלה גרורתית.
⚠️ חסר מידע מפורש על דירוג הסיכון.

טיפול נוכחי:
דרוש: טיפול אנדוקריני מסוג טמוקסיפן או אנאסטרוזול.
המטופלת: נוטלת אנאסטרוזול.
✔️ מתאים.

---

כעת נתח את המידע הבא:

קריטריוני מחקר:
{extracted_criteria}

מידע רפואי של המטופל:
{all_medical_text[:6000]}

אנא נתח האם המטופלת מתאימה להשתתף במחקר הקליני, תוך שימוש בשפה מקצועית, רפואית, בהירה וזורמת – כפי שמוסבר לרופא עמית. אל תשתמש בסמלים כמו ✅ או ❌. פרט אילו קריטריוני הכללה ואי הכללה מתקיימים ואילו לא, תוך הסבר קצר לכל אחד. ציין גם אם חסר מידע חשוב.
במידה ולא נמצאו קריטריוני אי-הכללה רלוונטיים – כתוב זאת במפורש


- הימנע משילוב של מילים באנגלית באמצע משפטים בעברית. תרגם הכל לעברית תקנית וברורה.
בסיום, נסח פסקת מסקנה ברורה: האם ניתן להסיק התאמה למחקר, ואם לא – מה נדרש כדי לקבל החלטה.
"""



        # Get response
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": matching_prompt}]
        ).choices[0].message.content

        # Show result
        st.subheader("🧠 תוצאת ההתאמה:")
        st.markdown(response)
