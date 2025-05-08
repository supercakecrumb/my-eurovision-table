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
            return redirect(url_for('index'))  # Fixed: redirect to index instead of login

        stage = Stage.query.get_or_404(stage_id)
        user_id = session['user_id']

        grades = {grade.country_id: grade.value for grade in
                  Grade.query.filter_by(user_id=user_id, stage_id=stage_id).all()}

        # Fetch sum of grades for each country in this stage from all users
        rankings = db.session.query(
            Country.id,
            db.func.sum(Grade.value).label('total_grade')
        ).join(Grade).filter(Grade.stage_id == stage_id).group_by(Country.id).order_by(
            db.func.sum(Grade.value).desc()).all()

        # Create a dictionary of country_id to total_grade for sorting
        country_scores = {country_id: total_grade for country_id, total_grade in rankings}
        
        # Get all countries in this stage
        countries_in_stage = Country.query.join(Stage.countries).filter(Stage.id == stage_id).all()
        
        # Sort countries by their total score (if they have votes)
        # Countries with no votes will be at the end in their original order
        sorted_countries = sorted(
            countries_in_stage,
            key=lambda country: country_scores.get(country.id, 0),
            reverse=True
        )

        ranking_items = [(Country.query.get(country_id), total_grade) for country_id, total_grade in rankings]

        return render_template('stage.html', stage=stage, countries=sorted_countries, grades=grades,
                               ranking_items=ranking_items)

    @app.route('/stage/<int:stage_id>/submit/<int:country_id>', methods=['POST'])
    def submit_grades(stage_id, country_id):
        if 'user_id' not in session:
            flash("Please log in to vote", "warning")
            return redirect(url_for('index'))  # Fixed: redirect to index instead of login

        user_id = session['user_id']
        # Convert grade_value to integer
        try:
            grade_value = int(request.form.get('grade'))
            # Validate grade is within allowed range
            if not 1 <= grade_value <= 12:
                flash("Grade must be between 1 and 12", "danger")
                return redirect(url_for('stage', stage_id=stage_id))
        except (ValueError, TypeError):
            flash("Invalid grade value", "danger")
            return redirect(url_for('stage', stage_id=stage_id))

        existing_grade = Grade.query.filter_by(user_id=user_id, stage_id=stage_id, country_id=country_id).first()

        if existing_grade:
            existing_grade.value = grade_value
        else:
            new_grade = Grade(user_id=user_id, stage_id=stage_id, country_id=country_id, value=grade_value)
            db.session.add(new_grade)

        db.session.commit()
        flash("Your vote has been recorded!", "success")
        return redirect(url_for('stage', stage_id=stage_id))