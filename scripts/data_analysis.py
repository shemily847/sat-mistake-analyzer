import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PERCENTILE_LOOKUP = {1600: 99, 1400: 95, 1200: 75, 1000: 50, 800: 25, 600: 5, 400: 1}

def estimate_percentile(total_score):
    for score, percentile in sorted(PERCENTILE_LOOKUP.items(), reverse=True):
        if total_score >= score:
            return percentile
    return 1

def calculate_scores(df):
    df['Correct'] = df['Student_Answer'] == df['Correct_Answer']
    rw_data = df[df['Section'] == 'Reading and Writing']
    math_data = df[df['Section'] == 'Math']

    rw_module1 = rw_data[rw_data['Module'] == 'Module 1']
    rw_module2 = rw_data[rw_data['Module'] == 'Module 2']
    math_module1 = math_data[math_data['Module'] == 'Module 1']
    math_module2 = math_data[math_data['Module'] == 'Module 2']

    rw_correct_m1 = rw_module1['Correct'].sum()
    rw_correct_m2 = rw_module2['Correct'].sum()
    math_correct_m1 = math_module1['Correct'].sum()
    math_correct_m2 = math_module2['Correct'].sum()

    rw_correct = rw_correct_m1 + rw_correct_m2
    math_correct = math_correct_m1 + math_correct_m2

    rw_scaled = 200 + (rw_correct / 54) * 600
    math_scaled = 200 + (math_correct / 44) * 600

    rw_m1_accuracy = rw_correct_m1 / 27 if len(rw_module1) > 0 else 0
    math_m1_accuracy = math_correct_m1 / 22 if len(math_module1) > 0 else 0

    if rw_m1_accuracy >= 0.7:
        rw_scaled += 50
    if math_m1_accuracy >= 0.7:
        math_scaled += 50

    rw_scaled = min(800, max(200, int(rw_scaled)))
    math_scaled = min(800, max(200, int(math_scaled)))

    total_score = rw_scaled + math_scaled
    percentile = estimate_percentile(total_score)

    return {
        'rw_correct': rw_correct,
        'math_correct': math_correct,
        'rw_scaled': rw_scaled,
        'math_scaled': math_scaled,
        'total_score': total_score,
        'percentile': percentile
    }

def map_to_content_domain(row):
    section = row['Section']
    topic = row['Topic']

    if section == 'Reading and Writing':
        if topic in ['Central Ideas and Details', 'Command of Evidence (Textual)', 'Command of Evidence (Quantitative)', 'Inferences']:
            return "Information and Ideas"
        elif topic in ['Words in Context', 'Text Structure and Purpose', 'Cross-Text Connections']:
            return "Craft and Structure"
        elif topic in ['Rhetorical Synthesis', 'Transitions']:
            return "Expression of Ideas"
        elif topic in ['Boundaries', 'Form/Structure/Sense']:
            return "Standard English Conventions"
        else:
            return "Unknown (Reading and Writing)"
    elif section == 'Math':
        if topic in ['Algebra']:
            return "Algebra"
        elif topic in ['Advanced Math']:
            return "Advanced Math"
        elif topic in ['Problem Solving and Data Analysis']:
            return "Problem-Solving and Data Analysis"
        elif topic in ['Geometry', 'Trigonometry']:
            return "Geometry and Trigonometry"
        else:
            return "Unknown (Math)"
    return "Unknown"

def analyze_mistakes(df):
    # Ensure required columns exist
    required_columns = ['Question_ID', 'Section', 'Module', 'Topic', 'Student_Answer', 'Correct_Answer', 'Difficulty']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df['Correct'] = df['Student_Answer'] == df['Correct_Answer']

    # Map topics to content domains
    df['Content_Domain'] = df.apply(map_to_content_domain, axis=1)

    # Calculate scores (based on all questions)
    scores = calculate_scores(df)

    # Filter to only include mistakes (where Correct is False) for mistake analysis
    mistakes_df = df[df['Correct'] == False]

    if mistakes_df.empty:
        # Return empty results if there are no mistakes
        return {
            'mistakes_by_section': pd.DataFrame(columns=['Section', 'Mistakes']),
            'mistakes_by_topic': pd.DataFrame(columns=['Section', 'Topic', 'Module', 'Mistakes', 'Avg_Difficulty', 'Weighted_Mistakes']),
            'mistakes_by_domain': pd.DataFrame(columns=['Section', 'Content_Domain', 'Module', 'Mistakes']),
            'top_mistakes': pd.DataFrame(columns=['Section', 'Topic', 'Weighted_Mistakes']),
            'scores': scores
        }

    # Calculate mistakes by section
    mistakes_by_section = mistakes_df.groupby('Section')['Student_Answer'].count().reset_index()
    mistakes_by_section.columns = ['Section', 'Mistakes']

    # Calculate mistakes by topic
    mistakes_by_topic = mistakes_df.groupby(['Section', 'Topic', 'Module']).agg({
        'Student_Answer': 'count',
        'Difficulty': lambda x: pd.Series(x).map({'Easy': 1, 'Medium': 2, 'Hard': 3}).mean()
    }).reset_index()
    mistakes_by_topic.columns = ['Section', 'Topic', 'Module', 'Mistakes', 'Avg_Difficulty']
    mistakes_by_topic['Weighted_Mistakes'] = mistakes_by_topic['Mistakes'] * mistakes_by_topic['Avg_Difficulty']

    # Calculate mistakes by content domain
    mistakes_by_domain = mistakes_df.groupby(['Section', 'Content_Domain', 'Module'])['Student_Answer'].count().reset_index()
    mistakes_by_domain.columns = ['Section', 'Content_Domain', 'Module', 'Mistakes']

    # Calculate top mistakes (by Topic for granularity in study plan)
    top_mistakes = mistakes_by_topic.sort_values(by='Weighted_Mistakes', ascending=False).head(5)

    return {
        'mistakes_by_section': mistakes_by_section,
        'mistakes_by_topic': mistakes_by_topic,
        'mistakes_by_domain': mistakes_by_domain,
        'top_mistakes': top_mistakes,
        'scores': scores
    }

def plot_mistakes_by_type(mistakes_by_domain):
    plt.figure(figsize=(10, 6))
    sns.barplot(data=mistakes_by_domain, x='Content_Domain', y='Mistakes', hue='Section', style='Module', palette="Blues_r")
    plt.title("Mistakes by Content Domain Across Sections and Modules")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.gcf()