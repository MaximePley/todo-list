from app import app, db
from app.email import send_password_reset_email
from app.forms import TaskForm, LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, ProjectForm, CancelForm, YesForm
from app.models import User, Task, Project
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from bs4 import BeautifulSoup


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # soup = BeautifulSoup('D:/Webpage/2-Application/Todo_list/app/templates/index.html', 'html.parser')
    tasks = {}
    form = TaskForm()
    projects = User.user_projects(current_user)
    # print(soup.find('input', {'name': 'Task n1'}).attr('checked'))
    for p in projects:
        tasks.update({p.title: Project.getProjectTasks(p)})
    # print(soup.find('input', {'name': 'task 85'}))
    # inputTags = soup.findAll(attrs={"name": "task 85"})
    # output = [x["task 85"] for x in inputTags]
    # print(soup.prettify())
    return render_template("index.html", title='Home Page', form=form, tasks=tasks)


@app.route('/project/<projectname>', methods=['GET', 'POST'])
@login_required
def projectedit(projectname):
    project = Project.query.filter_by(title=projectname).first_or_404()
    task = Project.projectEdit(project).tasks
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(body=form.label.data, project=project, checked='unchecked')
        db.session.add(task)
        db.session.commit()
        flash('Your task is now live!')
        task = Project.projectEdit(project).tasks
    return render_template('project.html', project=project, form=form, task=task)


@app.route('/add_project', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data, owner=current_user)
        db.session.add(project)
        db.session.commit()
        flash('New project created')
        return redirect(url_for('index'))
    return render_template('add_project.html', title='New project', form=form)


@app.route('/delete_project', methods=['GET', 'POST'])
@login_required
def delete_project():
    form = CancelForm()
    projects = User.user_projects(current_user)
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template('delete_project.html', title='Delete project', form=form, projects=projects)


@app.route('/confirm_deletion/<projectid>', methods=['GET', 'POST'])
@login_required
def confirm_deletion(projectid):
    form = YesForm()
    project = Project.query.filter_by(id=projectid).first()
    if form.validate_on_submit():
        for t in project.tasks:
            db.session.delete(t)
        db.session.delete(project)
        db.session.commit()
        projects = User.user_projects(current_user)
        form = CancelForm()
        return redirect(url_for('delete_project'))
    return render_template('confirm_deletion.html', form=form, project=project.title)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html')


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html')


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
