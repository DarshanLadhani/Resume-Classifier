import streamlit as st
import pickle
import re
import warnings
from pdfminer.high_level import extract_text

warnings.filterwarnings('ignore',category=UserWarning)
warnings.filterwarnings('ignore',category=SyntaxWarning)
warnings.filterwarnings('ignore',category=FutureWarning)

# loading models
clf = pickle.load(open('clf.pkl','rb'))
tdif = pickle.load(open('tdif.pkl','rb'))

def extract_text_from_pdf(file):
    text = extract_text(file)
    return text

# Clean Fucntion 
def clean(resume_text): 
    clean_text = re.sub('http\S+\s*', ' ', resume_text)
    clean_text = re.sub('RT|cc', ' ', clean_text)
    clean_text = re.sub('#\S+', '', clean_text)
    clean_text = re.sub('@\S+', '  ', clean_text)
    clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
    clean_text = re.sub(r'[^\x00-\x7f]', r' ', clean_text)   
    clean_text = re.sub('\s+', ' ', clean_text)

    return clean_text

# Checking if uploaded file is resume or not
def is_resume(text):
    text = text.lower()
    count = 0
    for word in resumes_words: 
        if word in text:
            count+=1
    return count>=3

# Map category ID to category name
category_mapping = {19: 'HR',
 13: 'DESIGNER',
 20: 'INFORMATION-TECHNOLOGY',
 23: 'TEACHER',
 1: 'ADVOCATE',
 9: 'BUSINESS-DEVELOPMENT',
 18: 'HEALTHCARE',
 17: 'FITNESS',
 2: 'AGRICULTURE',
 8: 'BPO',
 22: 'SALES',
 12: 'CONSULTANT',
 14: 'DIGITAL-MEDIA',
 5: 'AUTOMOBILE',
 10: 'CHEF',
 16: 'FINANCE',
 3: 'APPAREL',
 15: 'ENGINEERING',
 0: 'ACCOUNTANT',
 11: 'CONSTRUCTION',
 21: 'PUBLIC-RELATIONS',
 7: 'BANKING',
 4: 'ARTS',
 6: 'AVIATION'}

resumes_words = ['experience','skills','education','email','name','contact']

# Web app
def main():
    st.title("Resume Screening App")
    uploaded_file = st.file_uploader("Upload Your Resume",type=['txt','pdf'])

    if uploaded_file is not None:
        try:
            if uploaded_file.type == 'text/plain':
                resume_text = uploaded_file.read().decode('utf-8')
                if resume_text is None:
                    st.write("The file is empty. Please a upload a proper resume file")
                    return
            elif uploaded_file.type == 'application/pdf':
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text is None:
                    st.write("The file is empty. Please a upload a proper resume file")
                    return
            else:
                st.error("Unsupported file format. Please upload a text file (.txt) or a PDF file (.pdf)")
                return
            
            if not is_resume(resume_text):
                st.write("This file does not appear to be a resume. Please upload a proper resume.")
                return

        except UnicodeDecodeError:
            resume_text = uploaded_file.read().decode('latin-1')
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
            return

        cleaned_resume = clean(resume_text)
        input_features = tdif.transform([cleaned_resume])
        prediction = clf.predict(input_features)[0]
        pred_category = category_mapping.get(prediction,"Unknown")
        st.write("Predicted Category : ",pred_category)

if __name__ == "__main__":
    main()