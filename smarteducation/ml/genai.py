import openai
from django.conf import settings


def generate_student_insight(student_data):
    """Generate AI insight for a student using OpenAI API."""
    if not settings.OPENAI_API_KEY:
        return "AI insights are not configured. Please set the OPENAI_API_KEY in settings."

    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        Analyze the following student data and provide actionable insights and recommendations:

        Student Name: {student_data.get('name', 'N/A')}
        Attendance: {student_data.get('attendance', 'N/A')}%
        Average Marks: {student_data.get('marks', 'N/A')}
        Grade: {student_data.get('grade', 'N/A')}
        Recent Marks Trend: {student_data.get('marks_trend', 'N/A')}
        Total Exams: {student_data.get('total_exams', 'N/A')}

        Please provide:
        1. Performance Summary
        2. Strengths
        3. Areas for Improvement
        4. Specific Recommendations
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational analytics AI assistant. Provide concise, actionable insights about student performance."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating AI insight: {str(e)}"


def generate_at_risk_intervention(student_data):
    """Generate intervention suggestions for at-risk students."""
    if not settings.OPENAI_API_KEY:
        return "AI insights are not configured. Please set the OPENAI_API_KEY in settings."

    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""
        This student has been identified as at-risk. Suggest specific interventions:

        Student Name: {student_data.get('name', 'N/A')}
        Attendance: {student_data.get('attendance', 'N/A')}%
        Average Marks: {student_data.get('marks', 'N/A')}
        Risk Level: {student_data.get('risk_level', 'N/A')}
        Key Issues: {student_data.get('issues', 'N/A')}

        Provide 3-5 specific intervention strategies.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an educational intervention specialist. Suggest practical, evidence-based intervention strategies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating intervention suggestions: {str(e)}"
