# SAT Mistake Analyzer

**SAT Mistake Analyzer** is a web-based tool that allows students to upload their SAT practice results, receive detailed analysis of their mistakes, track their progress over time, and download personalized study plans. Originally developed to support private tutoring sessions, the platform now offers a scalable solution for SAT preparation.

---

## 🔧 Features

### 1. Student Data Input & Management
- Upload SAT practice test results as CSV files (1 student per file).
- Automatically stores data using the student’s name or ID.
- Required columns:  
  `Question_ID, Section, Module, Topic, Student_Answer, Correct_Answer, Difficulty`

### 2. Practice Test Analysis (Analysis Tab)
- Calculates Reading & Writing, Math, and Total scores (400–1600).
- Provides percentile estimates.
- Identifies common mistakes by Section, Content Domain, and Topic.
- Applies weighted scoring based on question difficulty.
- Visualizes:
  - Top 5 weakest topics
  - Mistakes by Content Domain and Module
- Generates a personalized study plan based on mistake weight.

### 3. Progress Tracking (Progress Tab)
- Saves each analysis session to `history.json`.
- Tracks score, percentile, and mistake trends over time.
- Visualizes:
  - Score trends by date
  - Mistake trends by Content Domain
- Provides a performance comparison table with color-coded changes.

### 4. Report Generation
- Exports a full PDF report with name, scores, and study recommendations.
- Allows users to download `history.json` to maintain progress across sessions.

### 5. User-Friendly Experience
- Sidebar includes CSV format instructions and error handling.
- Student’s name appears in all headers for a personalized feel.
- Optional: Add sample CSV for download.

### 6. Deployment
- Hosted on Streamlit Community Cloud:  
  👉 https://sat-mistake-analyzer-forstudent.streamlit.app
- GitHub-hosted project with downloadable reports and local setup support.

---

## 📁 Project Structure

```
.
├── app.py
├── requirements.txt
├── history.json
├── /scripts
│   ├── data_analysis.py
│   ├── explanations.py
│   ├── export_report.py
│   ├── practice_questions.py
│   └── study_plan.py
```

---

## 🛠 Tech Stack

- Python
- Streamlit
- Pandas, Seaborn, Matplotlib, Plotly
- ReportLab (for PDF export)

---

## 🙋‍♀️ About the Creator

Built by **Emily Kim** — SAT tutor and aspiring product manager with a passion for educational tools and user-focused analytics.  
This project combines personal tutoring experience with data science and product design.

---

## Contact
seohyon847@gmail.com
🌐 https://github.com/shemily847
