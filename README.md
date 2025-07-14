# Resume-Analyser
**Resume-Analyser** is a smart web application that evaluates your resume’s effectiveness for a specific job description. Using NLP and keyword matching, it provides personalized feedback to improve your chances of getting shortlisted by Applicant Tracking Systems (ATS).
---
## 📸 Images

![Screenshot 1](https://github.com/RishulGupta/Resume-Analyser/blob/010f521727feeb03c524d0596e617071a46dba1d/Screenshot%202025-07-11%20224823.png)  
*Resume upload and input interface*

![Screenshot 2](https://github.com/RishulGupta/Resume-Analyser/blob/010f521727feeb03c524d0596e617071a46dba1d/Screenshot%202025-07-11%20224854.png)  
*Results with scoring and suggestions*


---

## 🧠 Features

- ✅ **ATS Compatibility Score** – Checks formatting, sections, and structure  
- 🔍 **Job Matching Score** – Compares resume against the job description  
- 🗝️ **Keyword Gap Analysis** – Identifies missing but important keywords  
- 📄 **Resume Highlights** – Extracts skills, experience, education  
- 💡 **Improvement Suggestions** – Personalized advice to improve your resume  

---



## 🛠️ Tech Stack

- **Frontend**: HTML, CSS, JavaScript  
- **Backend**: Python (Flask or FastAPI)  
- **NLP Engine**: spaCy / OpenAI (optional)  
- **Resume Parsing**: `pdfminer.six`, `python-docx`  
- **Deployment**: Render / Vercel / Heroku  

---

## 📦 How to run 

# Clone the repository
git clone https://github.com/RishulGupta/Resume-Analyser.git

cd Resume-Analyser

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate 
On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

