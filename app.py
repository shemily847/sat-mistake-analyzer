import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import date
from scripts.data_analysis import analyze_mistakes, plot_mistakes_by_type
from scripts.study_plan import generate_study_plan
from scripts.export_report import export_pdf

# Set page config for a wider layout and custom theme
st.set_page_config(page_title="SAT Mistake Analyzer", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a cleaner UI
st.markdown("""
    <style>
    .main {background-color: #f5f7fa;}
    .stSidebar {background-color: #e6ecf0;}
    h1 {color: #2c3e50; font-family: 'Arial', sans-serif;}
    h2, h3 {color: #34495e; font-family: 'Arial', sans-serif;}
    .stButton>button {background-color: #3498db; color: white; border-radius: 5px;}
    .stButton>button:hover {background-color: #2980b9;}
    .stDataFrame {border: 1px solid #d3d3d3; border-radius: 5px;}
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation and input
with st.sidebar:
    st.header("SAT Mistake Analyzer")
    st.markdown("""
    **Instructions:**
    1. Enter your Student ID or Name.
    2. Upload a CSV file with your SAT practice test data.
    3. The CSV should include the following columns:
       - Question_ID, Section, Module, Topic, Student_Answer, Correct_Answer, Difficulty
    4. The tool will analyze your mistakes and show your progress over time.
    """)
    student_name = st.text_input("Enter Student ID or Name", placeholder="e.g., JohnDoe123").strip()
    file = st.file_uploader("Upload Your SAT Score Report (CSV)", type=["csv"], help="Upload a CSV with your SAT practice data.")
    st.markdown("---")
    st.markdown("**Navigation**")
    tab_selection = st.radio("Go to:", ["Analysis", "Progress"])
    st.markdown("---")
    st.markdown("**About**")
    st.info("This tool analyzes your SAT practice data, tracks progress, and provides insights to improve your score.")

# Main content
if file and student_name:
    try:
        df = pd.read_csv(file)
        analysis = analyze_mistakes(df)

        # Save history for trend analysis
        today = str(date.today())
        history_file = "history.json"

        # Prepare data to save
        today_results = {
            'mistakes': dict(zip(analysis['mistakes_by_topic']["Topic"], analysis['mistakes_by_topic']["Mistakes"])),
            'scores': analysis['scores'],
            'mistakes_by_domain': analysis['mistakes_by_domain'].groupby('Content_Domain')['Mistakes'].sum().to_dict()
        }

        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                full_history = json.load(f)
        else:
            full_history = {}

        if student_name not in full_history:
            full_history[student_name] = {}

        full_history[student_name][today] = today_results
        with open(history_file, "w") as f:
            json.dump(full_history, f, indent=4)

        # Generate study plan
        plan_dict = generate_study_plan(analysis['top_mistakes'])
        plan_str = "Study Plan:\n\n" + "\n".join([f"{topic}: {time}" for topic, time in plan_dict.items()])

        # Tab content
        if tab_selection == "Analysis":
            st.header(f"Analysis Dashboard for {student_name}")
            
            # Summary Section
            st.subheader("Summary")
            total_mistakes = analysis['mistakes_by_section']['Mistakes'].sum()
            st.write(f"You made **{total_mistakes} mistakes** in this test.")
            st.write(f"Your total score is **{analysis['scores']['total_score']}** ({analysis['scores']['percentile']}th percentile).")
            weakest_domain = analysis['mistakes_by_domain'].groupby('Content_Domain')['Mistakes'].sum().idxmax()
            st.write(f"Your weakest area is **{weakest_domain}**. Focus on this domain to improve your score.")

            # Current Scores
            st.subheader("Current Performance")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Score", f"{analysis['scores']['total_score']}", f"{analysis['scores']['percentile']}th Percentile")
            col2.metric("Reading & Writing", f"{analysis['scores']['rw_scaled']}")
            col3.metric("Math", f"{analysis['scores']['math_scaled']}")

            # Mistakes Overview
            st.subheader("Mistakes Overview")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("**Mistakes by Section**")
                st.dataframe(analysis['mistakes_by_section'], use_container_width=True)
            with col2:
                st.write("**Mistakes by Content Domain Across Sections and Modules**")
                st.dataframe(analysis['mistakes_by_domain'], use_container_width=True)

            # Detailed Topic Breakdown
            st.subheader("Topic Breakdown")
            for section in analysis['mistakes_by_topic']['Section'].unique():
                with st.expander(f"{section} Topics", expanded=True):
                    section_data = analysis['mistakes_by_topic'][analysis['mistakes_by_topic']['Section'] == section]
                    for module in section_data['Module'].unique():
                        st.write(f"**{module}**")
                        module_data = section_data[section_data['Module'] == module]
                        st.dataframe(module_data, use_container_width=True)

            # Visualizations
            st.subheader("Visual Insights")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write("**Top 5 Weaknesses (Weighted by Difficulty)**")
                fig = px.bar(
                    analysis['top_mistakes'],
                    x='Weighted_Mistakes',
                    y='Topic',
                    color='Section',
                    text='Weighted_Mistakes',
                    title="Top 5 Weaknesses",
                    height=400
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.write("**Mistakes by Content Domain**")
                st.pyplot(plot_mistakes_by_type(analysis['mistakes_by_domain']))

            # Study Plan
            st.subheader("Recommended Study Plan")
            for topic, time in plan_dict.items():
                st.write(f"- {topic}: {time}")

        else:  # Progress Tab
            st.header(f"Progress Tracker for {student_name}")
            history = full_history[student_name]
            
            if len(history) >= 1:
                dates = []
                total_scores = []
                rw_scores = []
                math_scores = []
                percentiles = []
                total_mistakes = []
                domain_mistakes = {domain: [] for domain in set(sum((list(data['mistakes_by_domain'].keys()) for data in history.values()), []))}

                for date, data in history.items():
                    dates.append(date)
                    total_scores.append(data['scores']['total_score'])
                    rw_scores.append(data['scores']['rw_scaled'])
                    math_scores.append(data['scores']['math_scaled'])
                    percentiles.append(data['scores']['percentile'])
                    total_mistakes.append(sum(data['mistakes'].values()))
                    for domain in domain_mistakes:
                        domain_mistakes[domain].append(data['mistakes_by_domain'].get(domain, 0))

                trends_df = pd.DataFrame({
                    'Date': dates,
                    'Total Score': total_scores,
                    'Reading and Writing Score': rw_scores,
                    'Math Score': math_scores,
                    'Percentile': percentiles,
                    'Total Mistakes': total_mistakes
                })

                # Score Trends
                st.subheader("Score Trends Over Time")
                fig = px.line(
                    trends_df,
                    x='Date',
                    y=['Total Score', 'Reading and Writing Score', 'Math Score'],
                    title="Score Trends",
                    markers=True,
                    height=400
                )
                fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)

                # Percentile and Total Mistakes Trends
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Percentile Trends**")
                    fig = px.line(
                        trends_df,
                        x='Date',
                        y='Percentile',
                        title="Percentile Trends",
                        markers=True,
                        color_discrete_sequence=['purple'],
                        height=300
                    )
                    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.write("**Total Mistakes Over Time**")
                    fig = px.line(
                        trends_df,
                        x='Date',
                        y='Total Mistakes',
                        title="Total Mistakes",
                        markers=True,
                        color_discrete_sequence=['red'],
                        height=300
                    )
                    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True)

                # Mistakes by Content Domain Trends
                st.subheader("Mistakes by Content Domain Over Time")
                domain_trends_df = pd.DataFrame(domain_mistakes)
                domain_trends_df['Date'] = dates
                fig = px.line(
                    domain_trends_df.melt(id_vars='Date', var_name='Content Domain', value_name='Mistakes'),
                    x='Date',
                    y='Mistakes',
                    color='Content Domain',
                    title="Mistakes by Content Domain Trends",
                    markers=True,
                    height=400
                )
                fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)

                # Comparison Table
                st.subheader("Performance Comparison")
                trends_df['Score Change'] = trends_df['Total Score'].diff()
                trends_df['Mistake Change'] = trends_df['Total Mistakes'].diff()
                trends_df['Score Trend'] = trends_df['Score Change'].apply(lambda x: "↑ Improved" if x > 0 else ("↓ Declined" if x < 0 else "No Change"))
                trends_df['Mistake Trend'] = trends_df['Mistake Change'].apply(lambda x: "↓ Improved" if x < 0 else ("↑ Increased" if x > 0 else "No Change"))
                trends_df_styled = trends_df.style.applymap(
                    lambda x: 'color: green' if 'Improved' in str(x) else ('color: red' if 'Declined' in str(x) or 'Increased' in str(x) else ''),
                    subset=['Score Trend', 'Mistake Trend']
                )
                st.dataframe(trends_df_styled, use_container_width=True)

        # Download Report Button
        st.markdown("---")
        if st.button("Download Report", help="Download a PDF report of your analysis"):
            pdf_file = export_pdf(student_name, analysis, plan_str)
            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")

    except Exception as e:
        st.error(f"Error processing your file: {str(e)}")
        st.info("Please ensure your CSV file has the correct columns: Question_ID, Section, Module, Topic, Student_Answer, Correct_Answer, Difficulty.")

else:
    st.info("Please enter your Student ID or Name and upload a CSV file to start analyzing your SAT performance.")