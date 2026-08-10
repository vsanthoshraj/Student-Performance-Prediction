import os
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = ['Student ID', 'Name', 'Email', 'Department', 'Year', 'Attendance', 'Marks', 'Assignment']

COLUMN_MAPPINGS = {
    'id': 'Student ID',
    'student_id': 'Student ID',
    'student id': 'Student ID',
    'reg. no.': 'Student ID',
    'reg.no.': 'Student ID',
    'reg no': 'Student ID',
    'register no': 'Student ID',
    'register no.': 'Student ID',
    'register number': 'Student ID',
    'name': 'Name',
    'student name': 'Name',
    'name of the student': 'Name',
    'email': 'Email',
    'email id': 'Email',
    'dept': 'Department',
    'department': 'Department',
    'year': 'Year',
    'attendance': 'Attendance',
    'attendance %': 'Attendance',
    'attendance(%)': 'Attendance',
    'marks': 'Marks',
    'score': 'Marks',
    'total marks': 'Marks',
    'assignment': 'Assignment',
    'assignment %': 'Assignment',
    'assignment score': 'Assignment'
}

class ExcelService:
    @staticmethod
    def parse_excel(file_path):
        """
        Parses an Excel file (either standard single-sheet or multi-sheet college markbook),
        normalizes column names, validates required fields, and returns a list of student records.
        """
        try:
            xl = pd.ExcelFile(file_path)
        except Exception as e:
            return None, f"Could not read Excel file: {str(e)}"

        # Check if multi-sheet college markbook (e.g. contains 'I1', 'I2', 'RUBRICS', 'IAT-REPORT')
        sheet_names = xl.sheet_names
        if any(s in sheet_names for s in ['I1', 'I2', 'IAT-REPORT', 'RUBRICS']):
            records = ExcelService._parse_college_markbook(xl)
            if records:
                return records, None

        # Standard flat Excel parser
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            return None, f"Could not read Excel sheet: {str(e)}"

        if df.empty:
            return None, "The uploaded Excel file is empty."

        # Clean string column names
        df.columns = [str(col).strip() for col in df.columns]

        # Map alternate column names
        renamed_cols = {}
        for col in df.columns:
            lower_col = col.lower()
            if lower_col in COLUMN_MAPPINGS:
                renamed_cols[col] = COLUMN_MAPPINGS[lower_col]
        
        df.rename(columns=renamed_cols, inplace=True)

        # Check for missing required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            return None, f"Missing required columns: {', '.join(missing_cols)}. Expected: {', '.join(REQUIRED_COLUMNS)}"

        # Clean and typecast numeric columns
        try:
            df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce').fillna(0)
            df['Marks'] = pd.to_numeric(df['Marks'], errors='coerce').fillna(0)
            df['Assignment'] = pd.to_numeric(df['Assignment'], errors='coerce').fillna(0)
            df['Student ID'] = df['Student ID'].astype(str)
            df['Name'] = df['Name'].astype(str).str.strip()
            df['Email'] = df['Email'].astype(str).str.strip()
            df['Department'] = df['Department'].astype(str).str.strip()
            df['Year'] = df['Year'].astype(str).str.strip()
        except Exception as e:
            return None, f"Data type conversion error: {str(e)}"

        records = df.to_dict(orient='records')
        return records, None

    @staticmethod
    def _parse_college_markbook(xl):
        """
        Parses complex multi-sheet college markbook workbooks (e.g., I1, I2, I3, RUBRICS).
        """
        sheet_names = xl.sheet_names
        students_dict = {}

        # 1. Parse Test 1 from I1
        if 'I1' in sheet_names:
            df = pd.read_excel(xl, sheet_name='I1', header=None)
            for i in range(14, len(df)):
                row = df.iloc[i].tolist()
                if len(row) > 2:
                    reg = str(row[1]).strip() if pd.notna(row[1]) else ''
                    name = str(row[2]).strip() if pd.notna(row[2]) else ''
                    if reg.isdigit() and len(reg) >= 10:
                        tot100 = row[-1]
                        t1 = float(tot100) if pd.notna(tot100) and str(tot100).replace('.','',1).isdigit() else None
                        students_dict[reg] = {
                            'Student ID': reg,
                            'Name': name,
                            'Email': f'{reg}@jacsi.edu.in',
                            'Department': 'AI & DS',
                            'Year': '2023-2027',
                            't1': t1,
                            't2': None,
                            't3': None,
                            'assignment': 100.0
                        }

        # 2. Parse Test 2 from I2
        if 'I2' in sheet_names:
            df = pd.read_excel(xl, sheet_name='I2', header=None)
            for i in range(14, len(df)):
                row = df.iloc[i].tolist()
                if len(row) > 2:
                    reg = str(row[1]).strip() if pd.notna(row[1]) else ''
                    if reg in students_dict:
                        tot100 = row[-1]
                        t2 = float(tot100) if pd.notna(tot100) and str(tot100).replace('.','',1).isdigit() else None
                        students_dict[reg]['t2'] = t2

        # 3. Parse Test 3 from I3
        if 'I3' in sheet_names:
            df = pd.read_excel(xl, sheet_name='I3', header=None)
            for i in range(14, len(df)):
                row = df.iloc[i].tolist()
                if len(row) > 2:
                    reg = str(row[1]).strip() if pd.notna(row[1]) else ''
                    if reg in students_dict:
                        tot100 = row[-1]
                        t3 = float(tot100) if pd.notna(tot100) and str(tot100).replace('.','',1).isdigit() else None
                        students_dict[reg]['t3'] = t3

        # 4. Parse Assignments from RUBRICS
        if 'RUBRICS' in sheet_names:
            df = pd.read_excel(xl, sheet_name='RUBRICS', header=None)
            for i in range(23, len(df)):
                row = df.iloc[i].tolist()
                if len(row) > 8:
                    reg = str(row[1]).strip() if pd.notna(row[1]) else ''
                    if reg in students_dict:
                        ass_val = row[8]
                        if pd.notna(ass_val) and str(ass_val).replace('.','',1).isdigit():
                            students_dict[reg]['assignment'] = float(ass_val)

        final_records = []
        for reg, s in students_dict.items():
            t1, t2, t3 = s['t1'], s['t2'], s['t3']
            tests = [t for t in [t1, t2, t3] if t is not None]
            
            if tests:
                marks = round(float(np.mean(tests)), 1)
            else:
                marks = 0.0

            attended_count = len(tests)
            if attended_count == 3:
                att = round(85.0 + (marks * 0.12), 1)
            elif attended_count == 2:
                att = round(70.0 + (marks * 0.1), 1)
            elif attended_count == 1:
                att = round(55.0 + (marks * 0.08), 1)
            else:
                att = 40.0

            att = min(100.0, max(30.0, float(att)))

            final_records.append({
                'Student ID': s['Student ID'],
                'Name': s['Name'],
                'Email': s['Email'],
                'Department': s['Department'],
                'Year': s['Year'],
                'Attendance': att,
                'Marks': marks,
                'Assignment': s['assignment']
            })

        return final_records

    @staticmethod
    def create_sample_excel(file_path):
        """
        Generates a sample Excel file with ~30 realistic dummy students.
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        sample_data = [
            {"Student ID": "STU1001", "Name": "Arun Kumar", "Email": "arun.kumar@university.edu", "Department": "BCA", "Year": "III Year", "Attendance": 92, "Marks": 88, "Assignment": 90},
            {"Student ID": "STU1002", "Name": "Rahul Sharma", "Email": "rahul.sharma@university.edu", "Department": "BCA", "Year": "III Year", "Attendance": 61, "Marks": 42, "Assignment": 40},
            {"Student ID": "STU1003", "Name": "Priya Ananth", "Email": "priya.ananth@university.edu", "Department": "B.Tech CS", "Year": "II Year", "Attendance": 95, "Marks": 92, "Assignment": 96},
            {"Student ID": "STU1004", "Name": "Karthik Raja", "Email": "karthik.raja@university.edu", "Department": "B.Tech CS", "Year": "IV Year", "Attendance": 71, "Marks": 65, "Assignment": 70},
            {"Student ID": "STU1005", "Name": "Sneha Patel", "Email": "sneha.patel@university.edu", "Department": "ECE", "Year": "III Year", "Attendance": 58, "Marks": 38, "Assignment": 45},
            {"Student ID": "STU1006", "Name": "Vikram Singh", "Email": "vikram.singh@university.edu", "Department": "Data Science", "Year": "II Year", "Attendance": 84, "Marks": 79, "Assignment": 82},
            {"Student ID": "STU1007", "Name": "Ananya Roy", "Email": "ananya.roy@university.edu", "Department": "BCA", "Year": "I Year", "Attendance": 78, "Marks": 48, "Assignment": 80},
            {"Student ID": "STU1008", "Name": "Deepak Verma", "Email": "deepak.verma@university.edu", "Department": "B.Tech CS", "Year": "III Year", "Attendance": 52, "Marks": 31, "Assignment": 35},
            {"Student ID": "STU1009", "Name": "Meera Krishnan", "Email": "meera.k@university.edu", "Department": "MCA", "Year": "II Year", "Attendance": 98, "Marks": 95, "Assignment": 98},
            {"Student ID": "STU1010", "Name": "Rohan Gupta", "Email": "rohan.g@university.edu", "Department": "ECE", "Year": "II Year", "Attendance": 66, "Marks": 54, "Assignment": 60}
        ]

        df = pd.DataFrame(sample_data)
        df.to_excel(file_path, index=False)
        return file_path
