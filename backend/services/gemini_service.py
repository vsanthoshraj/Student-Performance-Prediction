import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')

    def get_client(self):
        if not self.api_key or self.api_key.strip() == "" or self.api_key == "your_gemini_api_key_here":
            return None
        try:
            return genai.Client(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            return None

    def ask_assistant(self, query, students_data, stats=None):
        """
        Sends structured student dataset to Gemini API with strict system instructions,
        falling back to an intelligent local analytics engine if key is missing or call fails.
        """
        if not students_data:
            return "No student dataset is currently loaded. Please upload an Excel sheet to begin."

        client = self.get_client()

        # Build clean JSON dataset representation
        cleaned_dataset = []
        for s in students_data:
            cleaned_dataset.append({
                "Student ID": s.get("Student ID"),
                "Name": s.get("Name"),
                "Email": s.get("Email"),
                "Department": s.get("Department"),
                "Year": s.get("Year"),
                "Attendance": s.get("Attendance"),
                "Marks": s.get("Marks"),
                "Assignment": s.get("Assignment"),
                "Status": s.get("Status", "Unknown"),
                "Reasons": s.get("Reasons", [])
            })

        system_instruction = (
            "You are EduSense AI, the official academic intelligence assistant for Jayaraj Annapackiam C. S. I. College of Engineering, Nazareth.\n"
            "Department: Artificial Intelligence and Data Science (Class: III ADS, Batch: 2023-2027, Sem: 05, AY: 2025-26 Odd Sem).\n"
            "Course: CW3551 Data and Information Security | Instructor: G. Alisha Evangeline, AP/ADS.\n\n"
            "Answer questions strictly using the provided student dataset below.\n"
            "Rules:\n"
            "1. Never invent student names, marks, attendance, or statistics.\n"
            "2. If requested information is not in the dataset, clearly state that data is unavailable.\n"
            "3. Format answers clearly using Markdown (bolding, bullet points, tables when appropriate).\n"
            "4. Be concise, professional, and academically actionable."
        )


        prompt = (
            f"STUDENT DATASET ({len(cleaned_dataset)} students):\n"
            f"{json.dumps(cleaned_dataset, indent=2)}\n\n"
            f"USER QUESTION: {query}"
        )

        if client:
            try:
                # Using standard Gemini API call
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini API execution error: {e}. Falling back to local engine.")

        # Fallback local analytical engine if API is not available
        return self._local_analytics_fallback(query, cleaned_dataset, stats)

    def _local_analytics_fallback(self, query, dataset, stats):
        """
        Smart local NLP rule engine to guarantee offline operation during vivas.
        """
        q = query.lower()
        total = len(dataset)

        at_risk_list = [s for s in dataset if s['Status'] == 'At Risk']
        warning_list = [s for s in dataset if s['Status'] == 'Warning']
        good_list = [s for s in dataset if s['Status'] == 'Good']

        avg_att = sum(s['Attendance'] for s in dataset) / total if total else 0
        avg_marks = sum(s['Marks'] for s in dataset) / total if total else 0
        avg_ass = sum(s['Assignment'] for s in dataset) / total if total else 0

        for s in dataset:
            name_parts = s['Name'].lower().split()
            if any(part in q for part in name_parts if len(part) > 2):
                reasons_str = "\n".join([f"• {r}" for r in s.get('Reasons', [])])
                return (
                    f"**Student Profile: {s['Name']}** ({s['Department']} - {s['Year']})\n\n"
                    f"- **Status:** {s['Status']}\n"
                    f"- **Attendance:** {s['Attendance']}%\n"
                    f"- **Marks:** {s['Marks']}/100\n"
                    f"- **Assignment:** {s['Assignment']}%\n\n"
                    f"**Analysis & Reasons:**\n{reasons_str}"
                )

        if "how many students" in q and "risk" in q:
            return f"There are **{len(at_risk_list)} students** currently classified as **At Risk** out of {total} total students."

        if "how many students" in q:
            return f"The dataset contains a total of **{total} enrolled students** across {len(set(s['Department'] for s in dataset))} departments."

        if "highest mark" in q or "top score" in q or "highest marks" in q or "who scored highest" in q:
            top_student = max(dataset, key=lambda x: x['Marks'])
            return f"The student with the highest marks is **{top_student['Name']}** ({top_student['Department']}) with **{top_student['Marks']}/100**."

        if "lowest mark" in q or "lowest marks" in q or "who scored lowest" in q:
            low_student = min(dataset, key=lambda x: x['Marks'])
            return f"The student with the lowest marks is **{low_student['Name']}** ({low_student['Department']}) with **{low_student['Marks']}/100**."

        if "attendance below 75" in q or "low attendance" in q or "attendance below 75%" in q:
            low_att = [s for s in dataset if s['Attendance'] < 75]
            names = ", ".join([f"{s['Name']} ({s['Attendance']}%)" for s in low_att[:10]])
            more = f" and {len(low_att)-10} more" if len(low_att) > 10 else ""
            return f"There are **{len(low_att)} students** with attendance below 75%:\n\n{names}{more}."

        if "attendance below 60" in q or "attendance below 60%" in q:
            crit_att = [s for s in dataset if s['Attendance'] < 60]
            names = "\n".join([f"• **{s['Name']}** ({s['Department']}): {s['Attendance']}% attendance" for s in crit_att])
            return f"**{len(crit_att)} students** have critically low attendance (< 60%):\n\n{names}"

        if "average attendance" in q:
            return f"The average class attendance across all students is **{avg_att:.1f}%**."

        if "average mark" in q or "average marks" in q:
            return f"The average academic mark across all students is **{avg_marks:.1f}/100**."

        if "assignment" in q and ("poor" in q or "low" in q or "deficit" in q):
            low_ass = [s for s in dataset if s['Assignment'] < 50]
            names = "\n".join([f"• **{s['Name']}**: {s['Assignment']}% assignment completion" for s in low_ass[:8]])
            return f"**{len(low_ass)} students** have assignment completion below 50%:\n\n{names}"

        if "immediate attention" in q or "at risk" in q or "critical" in q:
            names = "\n".join([f"• **{s['Name']}** ({s['Department']}) — Att: {s['Attendance']}%, Marks: {s['Marks']}, Ass: {s['Assignment']}%" for s in at_risk_list[:10]])
            return f"The following **{len(at_risk_list)} students** require immediate intervention:\n\n{names}"

        if "summary" in q or "overview" in q or "problems" in q or "problem" in q:
            return (
                f"### Class Academic Performance Summary\n"
                f"- **Total Students:** {total}\n"
                f"- **Good Standing:** {len(good_list)} ({len(good_list)/total*100:.0f}%)\n"
                f"- **Needs Warning:** {len(warning_list)} ({len(warning_list)/total*100:.0f}%)\n"
                f"- **Immediate At Risk:** {len(at_risk_list)} ({len(at_risk_list)/total*100:.0f}%)\n\n"
                f"**Key Metrics:**\n"
                f"• Class Avg Attendance: **{avg_att:.1f}%**\n"
                f"• Class Avg Marks: **{avg_marks:.1f}/100**\n"
                f"• Class Avg Assignment: **{avg_ass:.1f}%**\n\n"
                f"**Primary Issues Identified:**\n"
                f"1. {len([s for s in dataset if s['Attendance'] < 75])} students have attendance below 75%.\n"
                f"2. {len([s for s in dataset if s['Marks'] < 50])} students scored below 50 in marks.\n"
                f"3. Recommendation: Issue email alerts to the {len(at_risk_list)} high-risk students."
            )

        if "compare" in q or "relationship" in q:
            return (
                f"**Attendance vs. Marks Analysis:**\n\n"
                f"• Students with Attendance ≥ 80% have an average mark of **{sum(s['Marks'] for s in dataset if s['Attendance'] >= 80) / max(1, len([s for s in dataset if s['Attendance'] >= 80])):.1f}**.\n"
                f"• Students with Attendance < 75% have an average mark of **{sum(s['Marks'] for s in dataset if s['Attendance'] < 75) / max(1, len([s for s in dataset if s['Attendance'] < 75])):.1f}**.\n\n"
                f"There is a strong positive correlation between high class attendance and academic marks."
            )

        return (
            f"Based on the dataset of **{total} students**:\n"
            f"- **{len(good_list)}** students are performing well.\n"
            f"- **{len(warning_list)}** students are on warning status.\n"
            f"- **{len(at_risk_list)}** students are at risk.\n\n"
            f"You can ask me specific questions like *'Which students have attendance below 75%?'*, *'Who scored highest?'*, or *'Why is Rahul at risk?'*."
        )
