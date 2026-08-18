import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from werkzeug.utils import secure_filename

# Ensure backend directory is in Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from database import db
from services.excel_service import ExcelService
from services.risk_service import RiskService
from services.gemini_service import GeminiService
from services.email_service import EmailService

app = Flask(
    __name__,
    template_folder=Config.TEMPLATE_FOLDER,
    static_folder=Config.STATIC_FOLDER
)
app.config.from_object(Config)

# Ensure required directories exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.DATA_FOLDER, exist_ok=True)

# Initialize Database on app load
db.init_db()

# Auto-seed ONLY real college dataset (Document from Santhosh Raj V.xlsx) into MySQL DB
real_data_path = os.path.join(Config.DATA_FOLDER, 'Document from Santhosh Raj V.xlsx')

if os.path.exists(real_data_path):
    db.clear_students()  # Wipe any old sample/fake data
    records, err = ExcelService.parse_excel(real_data_path)
    if records:
        r_service = RiskService()
        eval_students, _ = r_service.evaluate_dataset(records)
        db.save_students(eval_students)
        db.seed_default_users_and_semesters(eval_students)
        print(f"[EduSense] Loaded {len(eval_students)} official student records and 8 semester marksheets from Document from Santhosh Raj V.xlsx")

def get_current_risk_service():
    s_db = db.get_settings()
    att_t = int(s_db.get('attendance_threshold', Config.ATTENDANCE_THRESHOLD))
    marks_t = int(s_db.get('marks_threshold', Config.MARKS_THRESHOLD))
    ass_t = int(s_db.get('assignment_threshold', Config.ASSIGNMENT_THRESHOLD))
    return RiskService(att_t, marks_t, ass_t)

def get_current_gemini_service():
    s_db = db.get_settings()
    key = s_db.get('gemini_api_key', Config.GEMINI_API_KEY)
    return GeminiService(key)

def get_current_email_service():
    s_db = db.get_settings()
    srv = s_db.get('smtp_server', Config.SMTP_SERVER)
    port = s_db.get('smtp_port', Config.SMTP_PORT)
    usr = s_db.get('smtp_username', Config.SMTP_USERNAME)
    pwd = s_db.get('smtp_password', Config.SMTP_PASSWORD)
    snd = s_db.get('sender_email', Config.SENDER_EMAIL)
    return EmailService(srv, port, usr, pwd, snd)

@app.before_request
def check_auth():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'user' not in session:
        if request.endpoint is not None:
            return redirect(url_for('login'))
    
    # If logged in as student, restrict staff-only endpoints
    if session.get('role') == 'student':
        staff_only_routes = ['dashboard', 'upload', 'management', 'settings', 'alerts']
        if request.endpoint in staff_only_routes:
            return redirect(url_for('student_profile'))

@app.route('/')
def index():
    if session.get('role') == 'student':
        return redirect(url_for('student_profile'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username') or request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'staff') # 'staff' or 'student'

        user = db.authenticate_user(username, password, expected_role=role)
        if user:
            session['user'] = user.get('username')
            session['role'] = user.get('role', role)
            session['name'] = user.get('name', username)
            session['student_id'] = user.get('student_id')
            
            flash(f"Welcome back, {session['name']}!", 'success')
            if session['role'] == 'staff':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('student_profile'))
        else:
            # Demonstration Fallback Auth logic
            if role == 'staff' or (username and ('staff' in str(username).lower() or username in ['admin', 'staff@college.edu'])):
                session['user'] = 'staff@college.edu'
                session['role'] = 'staff'
                session['name'] = 'G. Alisha Evangeline, AP/ADS'
                session['student_id'] = None
                flash('Signed in as Staff In-Charge.', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Student fallback login using requested student ID or first student
                students = db.get_students()
                clean_un = str(username).strip() if username else ''
                target_id = clean_un if (clean_un and clean_un.isdigit()) else (students[0]['Student ID'] if students else '951323243001')
                target_student = db.get_student_by_id(target_id) or (students[0] if students else None)
                
                s_name = target_student['Name'] if target_student else 'Student'
                s_id = target_student['Student ID'] if target_student else '951323243001'

                session['user'] = s_id
                session['role'] = 'student'
                session['name'] = s_name
                session['student_id'] = s_id
                flash(f"Signed in as Student ({s_name}).", 'success')
                return redirect(url_for('student_profile'))
                
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    students_data = db.get_students()
    risk_srv = get_current_risk_service()
    students, stats = risk_srv.evaluate_dataset(students_data)

    has_data = len(students) > 0
    file_info = {
        'filename': 'Document from Santhosh Raj V.xlsx (MySQL)',
        'uploaded_at': 'Real-time'
    }

    return render_template('dashboard.html', students=students, stats=stats, file_info=file_info, has_data=has_data, active_page='dashboard')

@app.route('/student/profile')
@app.route('/student/profile/<student_id>')
def student_profile(student_id=None):
    # Determine target student ID
    if session.get('role') == 'student' or not student_id:
        target_id = session.get('student_id') or '951323243001'
    else:
        target_id = student_id

    raw_student = db.get_student_by_id(target_id)
    if not raw_student:
        # Fallback to first student if not found
        all_st = db.get_students()
        raw_student = all_st[0] if all_st else None
        if raw_student:
            target_id = raw_student['Student ID']

    if not raw_student:
        flash('Student record not found.', 'error')
        return redirect(url_for('dashboard'))

    # Evaluate risk
    risk_srv = get_current_risk_service()
    eval_res = risk_srv.evaluate_student(raw_student)
    student_info = dict(raw_student)
    student_info['Status'] = eval_res['status']
    student_info['StatusColor'] = eval_res['status_color']
    student_info['Reasons'] = eval_res['reasons']
    student_info['Recommendation'] = eval_res['recommendation']

    # Selected semester parameter (default to 5 or requested sem)
    selected_sem = request.args.get('sem', 5, type=int)

    # Fetch 8 semester summaries
    sem_summaries = db.get_student_sem_summaries(target_id)
    
    # Calculate Cumulative Overall Stats (CGPA & Overall Attendance)
    if sem_summaries:
        total_sgpa = sum([s['sgpa'] for s in sem_summaries])
        cgpa = round(total_sgpa / len(sem_summaries), 2)
        avg_att = round(sum([s['attendance'] for s in sem_summaries]) / len(sem_summaries), 1)
    else:
        cgpa = round(float(student_info.get('Marks', 70)) / 10.0, 2)
        avg_att = float(student_info.get('Attendance', 85))

    # Fetch subject marks for selected semester
    sem_marks = db.get_student_sem_marks(target_id, selected_sem)

    # All available students for quick switcher (if staff)
    all_students = db.get_students() if session.get('role') == 'staff' else []

    return render_template(
        'student_profile.html',
        student=student_info,
        sem_summaries=sem_summaries,
        sem_marks=sem_marks,
        selected_sem=selected_sem,
        cgpa=cgpa,
        overall_attendance=avg_att,
        all_students=all_students,
        active_page='student_profile'
    )

@app.route('/staff/enter-marks', methods=['POST'])
def staff_enter_marks():
    if session.get('role') != 'staff':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))
        
    student_id = request.form.get('student_id')
    sem_no = request.form.get('sem_no', 1, type=int)
    subject_code = request.form.get('subject_code')
    subject_name = request.form.get('subject_name')
    internal_marks = request.form.get('internal_marks', 0, type=float)
    external_marks = request.form.get('external_marks', 0, type=float)
    attendance = request.form.get('attendance', 90, type=float)
    credits = request.form.get('credits', 3, type=int)

    if not student_id or not subject_code or not subject_name:
        flash('Please fill in Student ID, Subject Code, and Subject Name.', 'error')
        return redirect(url_for('upload'))

    total_marks = round(internal_marks + external_marks, 1)
    
    if total_marks >= 90:
        grade = 'O'
    elif total_marks >= 80:
        grade = 'A+'
    elif total_marks >= 70:
        grade = 'A'
    elif total_marks >= 60:
        grade = 'B+'
    elif total_marks >= 50:
        grade = 'B'
    elif total_marks >= 45:
        grade = 'C'
    else:
        grade = 'U'

    marks_item = [{
        'subject_code': subject_code,
        'subject_name': subject_name,
        'internal_marks': internal_marks,
        'external_marks': external_marks,
        'total_marks': total_marks,
        'grade': grade,
        'attendance': attendance,
        'credits': credits
    }]

    db.save_student_sem_marks(student_id, sem_no, marks_item)

    # Re-calculate semester summary stats
    existing_marks = db.get_student_sem_marks(student_id, sem_no)
    if existing_marks:
        tot = sum([m['total_marks'] for m in existing_marks])
        avg = round(tot / len(existing_marks), 1)
        sgpa = round(min(10.0, max(4.0, (avg / 10.0) + 0.5)), 2)
        att = round(sum([m['attendance'] for m in existing_marks]) / len(existing_marks), 1)
        status = 'Pass' if avg >= 50 else 'Reappear'
        db.save_student_sem_summary(student_id, sem_no, tot, avg, sgpa, att, status)

    flash(f'Successfully saved marks for {subject_name} ({subject_code}) in Sem {sem_no}.', 'success')
    return redirect(url_for('upload'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    students_list = db.get_students()
    
    if request.method == 'POST':
        if 'excel_file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        file = request.files['excel_file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        sem_no = request.form.get('sem_no', 5, type=int)

        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)

            records, sem_map, err = ExcelService.parse_semester_excel(filepath, sem_no=sem_no)
            if err:
                flash(f'Excel Parsing Error: {err}', 'error')
            else:
                risk_srv = get_current_risk_service()
                evaluated_students, _ = risk_srv.evaluate_dataset(records)
                db.save_students(evaluated_students)
                
                # Save semester-wise marks & summaries
                if sem_map:
                    for s_id, s_data in sem_map.items():
                        db.save_student_sem_marks(s_id, s_data['sem_no'], s_data['subjects'])
                        db.save_student_sem_summary(
                            s_id, s_data['sem_no'], s_data['total_marks'],
                            s_data['avg_marks'], s_data['sgpa'], s_data['attendance'], s_data['status']
                        )

                flash(f'Successfully uploaded Semester {sem_no} Excel sheet & stored marks for {len(records)} students into MySQL database.', 'success')
                return redirect(url_for('upload'))
        else:
            flash('Invalid file format. Only .xlsx files are supported.', 'error')

    return render_template('upload.html', students=students_list, active_page='upload')

@app.route('/download-template')
@app.route('/download-template/<int:sem_no>')
def download_template(sem_no=1):
    batch = request.args.get('batch', '2026-2030')
    filename = f"EduSense_Semester_{sem_no}_Template_{batch.replace('-', '_')}.xlsx"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    ExcelService.generate_semester_excel_template(filepath, sem_no=sem_no, batch=batch)
    return send_file(filepath, as_attachment=True, download_name=filename)

@app.route('/staff/add-student', methods=['POST'])
def staff_add_student():
    student_id = request.form.get('student_id', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    department = request.form.get('department', 'AI & DS').strip()
    year = request.form.get('year', '2026-2030').strip()

    if not student_id or not name:
        flash('Student ID and Name are required.', 'error')
        return redirect(url_for('upload'))

    if not email:
        email = f"{student_id}@jacsi.edu.in"

    db.add_single_student(student_id, name, email, department, year)
    flash(f'Successfully added new student {name} ({student_id}) into Batch {year}. Student login created!', 'success')
    return redirect(url_for('upload'))


@app.route('/students')
def students():
    raw_students = db.get_students()
    risk_srv = get_current_risk_service()
    students_list, stats = risk_srv.evaluate_dataset(raw_students)

    departments = sorted(list(set([s.get('Department', 'General') for s in students_list])))
    return render_template('students.html', students=students_list, stats=stats, departments=departments, active_page='students')

@app.route('/student/<student_id>')
def student_detail(student_id):
    raw_student = db.get_student_by_id(student_id)
    if not raw_student:
        return jsonify({'error': 'Student not found.'}), 404

    risk_srv = get_current_risk_service()
    res = risk_srv.evaluate_student(raw_student)
    
    student_copy = dict(raw_student)
    student_copy['Status'] = res['status']
    student_copy['StatusColor'] = res['status_color']
    student_copy['Reasons'] = res['reasons']
    student_copy['Recommendation'] = res['recommendation']
    return jsonify(student_copy)

@app.route('/analytics')
def analytics():
    raw_students = db.get_students()
    risk_srv = get_current_risk_service()
    students_list, stats = risk_srv.evaluate_dataset(raw_students)

    dept_stats = {}
    for s in students_list:
        d = s.get('Department', 'General')
        if d not in dept_stats:
            dept_stats[d] = {'count': 0, 'good': 0, 'warning': 0, 'at_risk': 0}
        dept_stats[d]['count'] += 1
        st = s.get('Status')
        if st == 'Good':
            dept_stats[d]['good'] += 1
        elif st == 'Warning':
            dept_stats[d]['warning'] += 1
        else:
            dept_stats[d]['at_risk'] += 1

    return render_template('analytics.html', students=students_list, stats=stats, dept_stats=dept_stats, active_page='analytics')

@app.route('/alerts')
def alerts():
    raw_students = db.get_students()
    risk_srv = get_current_risk_service()
    students_list, _ = risk_srv.evaluate_dataset(raw_students)
    target_students = [s for s in students_list if s.get('Status') in ['At Risk', 'Warning']]
    return render_template('alerts.html', students=target_students, active_page='alerts')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        db.save_setting('attendance_threshold', request.form.get('attendance_threshold', Config.ATTENDANCE_THRESHOLD))
        db.save_setting('marks_threshold', request.form.get('marks_threshold', Config.MARKS_THRESHOLD))
        db.save_setting('assignment_threshold', request.form.get('assignment_threshold', Config.ASSIGNMENT_THRESHOLD))
        
        db.save_setting('gemini_api_key', request.form.get('gemini_api_key', ''))
        
        db.save_setting('smtp_server', request.form.get('smtp_server', ''))
        db.save_setting('smtp_port', request.form.get('smtp_port', '587'))
        db.save_setting('smtp_username', request.form.get('smtp_username', ''))
        db.save_setting('smtp_password', request.form.get('smtp_password', ''))
        db.save_setting('sender_email', request.form.get('sender_email', ''))

        flash('Settings updated successfully in MySQL database.', 'success')
        return redirect(url_for('settings'))

    s_db = db.get_settings()
    current_settings = {
        'attendance_threshold': s_db.get('attendance_threshold', Config.ATTENDANCE_THRESHOLD),
        'marks_threshold': s_db.get('marks_threshold', Config.MARKS_THRESHOLD),
        'assignment_threshold': s_db.get('assignment_threshold', Config.ASSIGNMENT_THRESHOLD),
        'gemini_api_key': s_db.get('gemini_api_key', Config.GEMINI_API_KEY),
        'smtp_server': s_db.get('smtp_server', Config.SMTP_SERVER),
        'smtp_port': s_db.get('smtp_port', Config.SMTP_PORT),
        'smtp_username': s_db.get('smtp_username', Config.SMTP_USERNAME),
        'smtp_password': s_db.get('smtp_password', Config.SMTP_PASSWORD),
        'sender_email': s_db.get('sender_email', Config.SENDER_EMAIL),
    }

    return render_template('settings.html', settings=current_settings, active_page='settings')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'answer': 'Please enter a valid question.'})

    raw_students = db.get_students()
    risk_srv = get_current_risk_service()
    students_list, stats = risk_srv.evaluate_dataset(raw_students)

    gemini_srv = get_current_gemini_service()
    answer = gemini_srv.ask_assistant(query, students_list, stats)
    return jsonify({'answer': answer})

@app.route('/api/send-email', methods=['POST'])
def api_send_email():
    data = request.get_json() or {}
    student_id = data.get('student_id')
    
    raw_student = db.get_student_by_id(student_id)
    if not raw_student:
        return jsonify({'success': False, 'message': 'Student not found.'}), 404

    risk_srv = get_current_risk_service()
    eval_res = risk_srv.evaluate_student(raw_student)
    raw_student['Status'] = eval_res['status']

    email_srv = get_current_email_service()
    success, msg = email_srv.send_alert(raw_student)
    if success:
        db.log_alert(student_id, raw_student.get('Email'), msg)
    return jsonify({'success': success, 'message': msg})

@app.route('/api/send-bulk-emails', methods=['POST'])
def api_send_bulk_emails():
    raw_students = db.get_students()
    risk_srv = get_current_risk_service()
    students_list, _ = risk_srv.evaluate_dataset(raw_students)

    email_srv = get_current_email_service()
    succ, fail, summary = email_srv.send_bulk_alerts(students_list)
    return jsonify({'success': True, 'message': summary, 'succeeded': succ, 'failed': fail})

@app.route('/api/load-sample', methods=['POST'])
def api_load_sample():
    real_path = os.path.join(Config.DATA_FOLDER, 'Document from Santhosh Raj V.xlsx')
    records, err = ExcelService.parse_excel(real_path)
    if err:
        return jsonify({'success': False, 'message': err}), 400

    db.clear_students()  # Wipe any existing data
    risk_srv = get_current_risk_service()
    eval_students, _ = risk_srv.evaluate_dataset(records)
    db.save_students(eval_students)
@app.route('/management')
def management():
    staffs = db.get_staffs()
    departments = db.get_departments()
    years = db.get_academic_years()
    return render_template('management.html', staffs=staffs, departments=departments, years=years, active_page='management')

@app.route('/api/staff/add', methods=['POST'])
def api_add_staff():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    designation = data.get('designation', '').strip()
    department = data.get('department', '').strip()
    email = data.get('email', '').strip()
    if not name or not designation or not department or not email:
        return jsonify({'success': False, 'message': 'All staff fields are required.'}), 400
    db.add_staff(name, designation, department, email)
    return jsonify({'success': True, 'message': f'Added staff member: {name}'})

@app.route('/api/staff/delete/<int:staff_id>', methods=['POST'])
def api_delete_staff(staff_id):
    db.delete_staff(staff_id)
    return jsonify({'success': True, 'message': 'Staff member deleted.'})

@app.route('/api/department/add', methods=['POST'])
def api_add_department():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    code = data.get('code', '').strip()
    hod = data.get('hod', '').strip()
    if not name or not code or not hod:
        return jsonify({'success': False, 'message': 'All department fields are required.'}), 400
    db.add_department(name, code, hod)
    return jsonify({'success': True, 'message': f'Added department: {name}'})

@app.route('/api/department/delete/<int:dept_id>', methods=['POST'])
def api_delete_department(dept_id):
    db.delete_department(dept_id)
    return jsonify({'success': True, 'message': 'Department deleted.'})

@app.route('/api/year/add', methods=['POST'])
def api_add_year():
    data = request.get_json() or {}
    year_name = data.get('year_name', '').strip()
    batch = data.get('batch', '').strip()
    if not year_name or not batch:
        return jsonify({'success': False, 'message': 'All year/batch fields are required.'}), 400
    db.add_academic_year(year_name, batch)
    return jsonify({'success': True, 'message': f'Added academic year: {year_name}'})

@app.route('/api/year/delete/<int:year_id>', methods=['POST'])
def api_delete_year(year_id):
    db.delete_academic_year(year_id)
    return jsonify({'success': True, 'message': 'Academic year deleted.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port, debug=True)


