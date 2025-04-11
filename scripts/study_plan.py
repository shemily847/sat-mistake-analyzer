def generate_study_plan(top_mistakes):
    plan = {}
    for _, row in top_mistakes.iterrows():
        topic = row['Topic']
        weighted_mistakes = row['Weighted_Mistakes']
        if weighted_mistakes > 5:
            time = "3 hours daily"
        elif weighted_mistakes > 2:
            time = "2 hours daily"
        else:
            time = "1 hour daily"
        plan[topic] = time
    return plan