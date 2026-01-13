from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# ==============================
# DATABASE CONFIG
# ==============================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==============================
# MODELS
# ==============================
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    courses = db.relationship('Course', backref='teacher', lazy=True)

    def __repr__(self):
        return f'<Teacher {self.name}>'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

# ==============================
# ROUTES
# ==============================

# Home - Students list
@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


# Courses list
@app.route('/courses')
def courses():
    courses_list = Course.query.all()
    return render_template('courses.html', courses=courses_list)


# Add Student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    courses = Course.query.all()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        new_student = Student(name=name, email=email, course_id=course_id)
        db.session.add(new_student)
        db.session.commit()

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html', courses=courses)


# Edit Student
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    courses = Course.query.all()
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', student=student, courses=courses)


# Delete Student
@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


# Add Course
@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    teachers = Teacher.query.all()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        teacher_id = request.form.get('teacher_id')

        new_course = Course(name=name, description=description, teacher_id=teacher_id)
        db.session.add(new_course)
        db.session.commit()

        flash('Course added successfully!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_course.html', teachers=teachers)


# Add Teacher
@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        new_teacher = Teacher(name=name, email=email)
        db.session.add(new_teacher)
        db.session.commit()

        flash('Teacher added successfully!', 'success')
        return redirect(url_for('courses'))

    return render_template('add_teacher.html')


# ==============================
# INIT DB
# ==============================
def init_db():
    with app.app_context():
        db.create_all()
        if Course.query.count() == 0:
            # Sample teachers
            t1 = Teacher(name='John Doe', email='john@example.com')
            t2 = Teacher(name='Jane Smith', email='jane@example.com')
            db.session.add_all([t1, t2])
            db.session.commit()

            # Sample courses
            courses = [
                Course(name='Python Basics', description='Learn Python fundamentals', teacher_id=t1.id),
                Course(name='Web Development', description='HTML, CSS, Flask', teacher_id=t2.id),
                Course(name='Data Science', description='Python for data analysis', teacher_id=t1.id)
            ]
            db.session.add_all(courses)
            db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
