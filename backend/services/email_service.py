import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None, sender=None):
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))
        self.username = username or os.getenv('SMTP_USERNAME', '')
        self.password = password or os.getenv('SMTP_PASSWORD', '')
        self.sender = sender or os.getenv('SENDER_EMAIL', self.username or 'edusense.alerts@university.edu')

    def generate_email_content(self, student):
        name = student.get('Name', 'Student')
        attendance = student.get('Attendance', 0)
        marks = student.get('Marks', 0)
        assignment = student.get('Assignment', 0)

        subject = "Academic Performance Alert"
        
        areas = []
        if attendance < 75:
            areas.append("• Attendance deficit")
        if marks < 50:
            areas.append("• Academic marks improvement needed")
        if assignment < 50:
            areas.append("• Pending assignment submissions")
            
        if not areas:
            areas = ["• General academic check-in"]

        areas_str = "\n".join(areas)

        body = (
            f"Dear {name},\n\n"
            f"This is an academic performance notification from EduSense.\n\n"
            f"Your current performance requires immediate attention:\n"
            f"• Attendance: {attendance:.0f}%\n"
            f"• Marks: {marks:.0f}/100\n"
            f"• Assignment: {assignment:.0f}%\n\n"
            f"Areas requiring improvement:\n"
            f"{areas_str}\n\n"
            f"Please take appropriate steps to improve your academic performance and contact your faculty advisor as soon as possible.\n\n"
            f"Regards,\n"
            f"EduSense Academic Intelligence\n"
            f"University Monitoring System"
        )

        return subject, body

    def send_alert(self, student):
        email_to = student.get('Email')
        if not email_to:
            return False, "Student does not have a valid email address."

        subject, body = self.generate_email_content(student)

        if not self.username or not self.password or self.username == "your_email@gmail.com":
            return True, f"Alert simulated for {student.get('Name')} ({email_to}). (SMTP credentials not configured in .env/Settings)."

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.sender, email_to, msg.as_string())
            server.quit()

            return True, f"Email alert successfully sent to {student.get('Name')} ({email_to})."
        except Exception as e:
            return False, f"Failed to send email to {email_to}: {str(e)}"

    def send_bulk_alerts(self, students_list):
        target_students = [s for s in students_list if s.get('Status') in ['At Risk', 'Warning']]
        
        if not target_students:
            return 0, 0, "No students requiring alerts were found."

        success_count = 0
        fail_count = 0
        details = []

        for student in target_students:
            success, msg = self.send_alert(student)
            if success:
                success_count += 1
            else:
                fail_count += 1
            details.append(msg)

        summary = f"Processed {len(target_students)} alerts ({success_count} succeeded, {fail_count} failed)."
        return success_count, fail_count, summary
