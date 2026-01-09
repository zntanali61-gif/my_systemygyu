from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employee
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hr_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('اسم المستخدم مسجل مسبقاً', 'warning')
        else:
            new_user = User(username=username, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('تم إنشاء الحساب بنجاح، يرجى تسجيل الدخول', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    employee_count = Employee.query.count()
    active_employees = Employee.query.filter_by(status='Active').count()
    # Mock data for charts or recent activities could be added here
    return render_template('dashboard.html', employee_count=employee_count, active_employees=active_employees)

@app.route('/employees')
@login_required
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

@app.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        department = request.form.get('department')
        job_title = request.form.get('job_title')
        salary = float(request.form.get('salary'))
        hire_date_str = request.form.get('hire_date')
        status = request.form.get('status')
        
        hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d')

        new_emp = Employee(full_name=full_name, phone=phone, 
                           department=department, job_title=job_title, 
                           salary=salary, hire_date=hire_date, status=status)
        db.session.add(new_emp)
        db.session.commit()
        flash('تم إضافة الموظف بنجاح', 'success')
        return redirect(url_for('employees'))
    return render_template('add_employee.html')

@app.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.full_name = request.form.get('full_name')
        employee.phone = request.form.get('phone')
        employee.department = request.form.get('department')
        employee.job_title = request.form.get('job_title')
        employee.salary = float(request.form.get('salary'))
        employee.hire_date = datetime.strptime(request.form.get('hire_date'), '%Y-%m-%d')
        employee.status = request.form.get('status')
        
        db.session.commit()
        flash('تم تحديث بيانات الموظف بنجاح', 'success')
        return redirect(url_for('employees'))
    return render_template('edit_employee.html', employee=employee)

@app.route('/employees/delete/<int:id>')
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('تم حذف الموظف بنجاح', 'success')
    return redirect(url_for('employees'))

if __name__ == '__main__':
    app.run(debug=True)
