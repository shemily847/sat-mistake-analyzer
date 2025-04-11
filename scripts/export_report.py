from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def export_pdf(student_name, analysis, plan):
    pdf_file = f"{student_name}_SAT_Analysis.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    
    elements = []
    
    elements.append(Paragraph(f"SAT Mistake Analysis for {student_name}", styles['Heading1']))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Current Scores", styles['Heading2']))
    elements.append(Paragraph(f"Total Score: {analysis['scores']['total_score']}", styles['Normal']))
    elements.append(Paragraph(f"Reading and Writing: {analysis['scores']['rw_scaled']}", styles['Normal']))
    elements.append(Paragraph(f"Math: {analysis['scores']['math_scaled']}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Study Plan", styles['Heading2']))
    elements.append(Paragraph(plan.replace('\n', '<br/>'), styles['Normal']))
    
    doc.build(elements)
    return pdf_file