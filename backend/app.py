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
# Clear any stale/fake sample data first to ensure only official records exist
real_data_path = os.path.join(Config.DATA_FOLDER, 'Document from Santhosh Raj V.xlsx')

if os.path.exists(real_data_path):
    db.clear_students()  # Wipe any old sample/fake data
    records, err = ExcelService.parse_excel(real_data_path)
    if records:
        r_service = RiskService()
        eval_students, _ = r_service.evaluate_dataset(records)
        db.save_students(eval_students)
        print(f"[EduSense] Loaded {len(eval_students)} official student records from Document from Santhosh Raj V.xlsx")

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

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            session['user'] = email
            flash('Successfully signed in.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter email and password.', 'error')
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

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'excel_file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        file = request.files['excel_file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)

            records, err = ExcelService.parse_excel(filepath)
            if err:
                flash(f'Excel Parsing Error: {err}', 'error')
            else:
                risk_srv = get_current_risk_service()
                evaluated_students, _ = risk_srv.evaluate_dataset(records)
                db.save_students(evaluated_students)
                flash(f'Successfully imported & stored {len(records)} students into MySQL database.', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid file format. Only .xlsx files are supported.', 'error')

    return render_template('upload.html', active_page='upload')

@app.route('/download-template')
def download_template():
    filepath = os.path.join(Config.DATA_FOLDER, 'Document from Santhosh Raj V.xlsx')
    return send_file(filepath, as_attachment=True, download_name='Document_from_Santhosh_Raj_V.xlsx')

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


