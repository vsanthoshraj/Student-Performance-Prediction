import os
from dotenv import load_dotenv

load_dotenv()

class RiskService:
    def __init__(self, attendance_threshold=None, marks_threshold=None, assignment_threshold=None):
        self.attendance_threshold = attendance_threshold or int(os.getenv('ATTENDANCE_THRESHOLD', 75))
        self.marks_threshold = marks_threshold or int(os.getenv('MARKS_THRESHOLD', 50))
        self.assignment_threshold = assignment_threshold or int(os.getenv('ASSIGNMENT_THRESHOLD', 50))

    def evaluate_student(self, student):
        """
        Evaluates student academic risk based on configurable rules.
        Returns status ('Good', 'Warning', 'At Risk'), reasons list, and recommended action.
        """
        attendance = float(student.get('Attendance', 0))
        marks = float(student.get('Marks', 0))
        assignment = float(student.get('Assignment', 0))

        reasons = []
        critical_issues = 0
        minor_issues = 0

        # Attendance check
        if attendance < 60:
            reasons.append(f"Critical low attendance: {attendance:.0f}% (well below {self.attendance_threshold}% threshold)")
            critical_issues += 1
        elif attendance < self.attendance_threshold:
            reasons.append(f"Attendance below threshold: {attendance:.0f}% (requires {self.attendance_threshold}%)")
            minor_issues += 1

        # Marks check
        if marks < 40:
            reasons.append(f"Critical low marks: {marks:.0f}/100 (well below {self.marks_threshold} threshold)")
            critical_issues += 1
        elif marks < self.marks_threshold:
            reasons.append(f"Marks below threshold: {marks:.0f}/100 (requires {self.marks_threshold})")
            minor_issues += 1

        # Assignment check
        if assignment < 40:
            reasons.append(f"Critical assignment deficit: {assignment:.0f}% (well below {self.assignment_threshold}% threshold)")
            critical_issues += 1
        elif assignment < self.assignment_threshold:
            reasons.append(f"Assignment completion low: {assignment:.0f}% (requires {self.assignment_threshold}%)")
            minor_issues += 1

        # Classification Logic
        if critical_issues > 0 or (minor_issues >= 2):
            status = 'At Risk'
            status_color = 'red'
        elif minor_issues == 1:
            status = 'Warning'
            status_color = 'orange'
        else:
            status = 'Good'
            status_color = 'green'
            reasons.append("Consistently meeting or exceeding all academic performance targets.")

        # Recommendation Generation
        recommendations = []
        if attendance < self.attendance_threshold:
            recommendations.append("Mandatory attendance tracking & faculty advising session.")
        if marks < self.marks_threshold:
            recommendations.append("Enrollment in peer tutoring & remedial subject coaching.")
        if assignment < self.assignment_threshold:
            recommendations.append("Submission of pending assignments before upcoming mid-term deadlines.")
        
        if not recommendations:
            recommendations.append("Maintain current performance and participate in advanced academic mentoring.")

        return {
            'status': status,
            'status_color': status_color,
            'reasons': reasons,
            'recommendation': " ".join(recommendations),
            'metrics': {
                'attendance': attendance,
                'marks': marks,
                'assignment': assignment
            }
        }

    def evaluate_dataset(self, students_list):
        """
        Processes a list of student records, adding risk metrics and summary stats.
        """
        evaluated_students = []
        stats = {
            'total': len(students_list),
            'good': 0,
            'warning': 0,
            'at_risk': 0,
            'avg_attendance': 0,
            'avg_marks': 0,
            'avg_assignment': 0,
            'attendance_counts': [0, 0, 0, 0, 0], # 0-50, 50-60, 60-75, 75-90, 90-100
            'marks_counts': [0, 0, 0, 0, 0]        # 0-40, 40-50, 50-70, 70-85, 85-100
        }

        tot_att = 0
        tot_marks = 0
        tot_ass = 0

        for student in students_list:
            res = self.evaluate_student(student)
            student_copy = dict(student)
            student_copy['Status'] = res['status']
            student_copy['StatusColor'] = res['status_color']
            student_copy['Reasons'] = res['reasons']
            student_copy['Recommendation'] = res['recommendation']
            
            evaluated_students.append(student_copy)

            if res['status'] == 'Good':
                stats['good'] += 1
            elif res['status'] == 'Warning':
                stats['warning'] += 1
            else:
                stats['at_risk'] += 1

            att = float(student.get('Attendance', 0))
            marks = float(student.get('Marks', 0))
            ass = float(student.get('Assignment', 0))

            tot_att += att
            tot_marks += marks
            tot_ass += ass

            # Binning attendance
            if att < 50:
                stats['attendance_counts'][0] += 1
            elif att < 60:
                stats['attendance_counts'][1] += 1
            elif att < 75:
                stats['attendance_counts'][2] += 1
            elif att < 90:
                stats['attendance_counts'][3] += 1
            else:
                stats['attendance_counts'][4] += 1

            # Binning marks
            if marks < 40:
                stats['marks_counts'][0] += 1
            elif marks < 50:
                stats['marks_counts'][1] += 1
            elif marks < 70:
                stats['marks_counts'][2] += 1
            elif marks < 85:
                stats['marks_counts'][3] += 1
            else:
                stats['marks_counts'][4] += 1

        if stats['total'] > 0:
            stats['avg_attendance'] = round(tot_att / stats['total'], 1)
            stats['avg_marks'] = round(tot_marks / stats['total'], 1)
            stats['avg_assignment'] = round(tot_ass / stats['total'], 1)

        return evaluated_students, stats
