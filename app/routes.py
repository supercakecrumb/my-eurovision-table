from flask import render_template, request, redirect, session, url_for, flash
from .models import db, User, Stage, Country, Grade
from .forms import LoginForm, GradeForm

def configure_routes(app):
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.')
        return redirect(url_for('index'))

    # Update existing routes to handle login status appropriately
    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()
            session['user_id'] = user.id
            session['username'] = username  # Store username in session for display
        stages = Stage.query.all()
        return render_template('index.html', form=form, stages=stages)

    @app.route('/stage/<int:stage_id>')
    def stage(stage_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Make sure you have a login route

        stage = Stage.query.get_or_404(stage_id)
        countries = Country.query.join(Stage.countries).filter(Stage.id == stage_id).all()
        user_id = session['user_id']

        # Fetch grades for each country in this stage for the current user
        grades = {grade.country_id: grade.value for grade in
                  Grade.query.filter_by(user_id=user_id, stage_id=stage_id).all()}

        # If no grades are present, initialize an empty dictionary or a default value
        if not grades:
            grades = {country.id: None for country in countries}  # Initialize with None or suitable default

        return render_template('stage.html', stage=stage, countries=countries, grades=grades)

    @app.route('/stage/<int:stage_id>/submit/<int:country_id>', methods=['POST'])
    def submit_grades(stage_id, country_id):
        if 'user_id' not in session:
            flash("Please log in to vote", "warning")
            return redirect(url_for('login'))

        user_id = session['user_id']
        grade_value = request.form.get('grade')

        existing_grade = Grade.query.filter_by(user_id=user_id, stage_id=stage_id, country_id=country_id).first()

        if existing_grade:
            existing_grade.value = grade_value
        else:
            new_grade = Grade(user_id=user_id, stage_id=stage_id, country_id=country_id, value=grade_value)
            db.session.add(new_grade)

        db.session.commit()
        flash("Your vote has been recorded!", "success")
        return redirect(url_for('stage', stage_id=stage_id))