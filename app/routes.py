from flask import render_template, request, redirect, session, url_for, flash, jsonify, json
from .models import db, User, Stage, Country, Grade
from .forms import LoginForm, GradeForm
from .country_flags import country_flags, get_flag_emoji
from datetime import datetime
import csv
import io

def configure_routes(app):
    # Register all routes with the app
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
            
            # Clear any existing session data
            session.pop('user_id', None)
            session.pop('username', None)
            
            # Find or create user
            user = User.query.filter_by(username=username).first()
            if not user:
                try:
                    user = User(username=username)
                    db.session.add(user)
                    db.session.commit()
                    flash(f"Welcome, {username}! Your account has been created.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error creating user: {str(e)}", "danger")
                    return render_template('index.html', form=form, stages=[])
            
            # Store user info in session
            session['user_id'] = user.id
            session['username'] = username
            flash(f"Welcome back, {username}!", "success")
            
        stages = Stage.query.all()
        return render_template('index.html', form=form, stages=stages)

    @app.route('/stage/<int:stage_id>')
    def stage(stage_id):
        if 'user_id' not in session:
            flash("Please log in to view stages", "warning")
            return redirect(url_for('index'))

        # Verify user exists in database
        user_id = session['user_id']
        user = User.query.get(user_id)
        if not user:
            flash("Your session has expired. Please log in again.", "danger")
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('index'))

        stage = Stage.query.get_or_404(stage_id)

        # Get the latest grade for each country
        latest_grades = db.session.query(
            Grade.country_id,
            db.func.max(Grade.timestamp).label('latest_timestamp')
        ).filter_by(
            user_id=user_id,
            stage_id=stage_id
        ).group_by(Grade.country_id).all()
        
        # Create a dictionary of country_id to grade value
        grades = {}
        for country_id, latest_timestamp in latest_grades:
            grade = Grade.query.filter_by(
                user_id=user_id,
                stage_id=stage_id,
                country_id=country_id,
                timestamp=latest_timestamp
            ).first()
            
            if grade:
                grades[country_id] = grade.value

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
        
        # Get all users for the users tab
        users = User.query.all()
        
        # Count votes per user for this stage
        user_votes = {}
        for user in users:
            vote_count = Grade.query.filter_by(user_id=user.id, stage_id=stage_id).count()
            user_votes[user.id] = vote_count
        
        # Find favorite country for each user (highest grade)
        user_favorites = {}
        for user in users:
            # Get the highest grade for this user in this stage
            highest_grade = db.session.query(
                Grade.country_id,
                Grade.value
            ).filter_by(
                user_id=user.id,
                stage_id=stage_id
            ).order_by(Grade.value.desc()).first()
            
            if highest_grade:
                country_id, _ = highest_grade
                user_favorites[user.id] = Country.query.get(country_id)

        return render_template('stage.html',
                              stage=stage,
                              countries=sorted_countries,
                              grades=grades,
                              ranking_items=ranking_items,
                              users=users,
                              user_votes=user_votes,
                              user_favorites=user_favorites,
                              country_flags=country_flags)
                              
    @app.route('/fill-db', methods=['GET', 'POST'])
    def fill_db():
        # Check if user is admin (for simplicity, we'll just check if they're logged in)
        if 'user_id' not in session:
            flash("You need to be logged in to access this page", "warning")
            return redirect(url_for('index'))
            
        # Verify user exists in database
        user_id = session['user_id']
        user = User.query.get(user_id)
        if not user:
            flash("Your session has expired. Please log in again.", "danger")
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('index'))
            
        # Initialize variables for template
        preview_data = None
        selected_stage = None
        clear_existing = False
        csv_data_json = None
        
        if request.method == 'POST':
            # Get form data
            stage_id = request.form.get('stage')
            clear_existing = 'clear_existing' in request.form
            
            # Map stage_id to actual stage names
            stage_map = {
                'semi1': 'Semi-final 1',
                'semi2': 'Semi-final 2',
                'final': 'Final'
            }
            
            selected_stage = stage_id
            stage_name = stage_map.get(stage_id)
            
            if not stage_name:
                flash("Invalid stage selected", "danger")
                return redirect(url_for('fill_db'))
                
            # Get CSV data from textarea
            csv_data_text = request.form.get('csv_data')
            
            if not csv_data_text or csv_data_text.strip() == '':
                flash("No CSV data provided", "danger")
                return redirect(url_for('fill_db'))
                
            # Read and validate CSV
            try:
                # Read CSV data from textarea
                stream = io.StringIO(csv_data_text, newline=None)
                csv_data = list(csv.DictReader(stream))
                
                # Validate CSV structure
                required_fields = ['country', 'artist', 'song']
                for field in required_fields:
                    if not all(field in row for row in csv_data):
                        flash(f"CSV is missing required field: {field}", "danger")
                        return redirect(url_for('fill_db'))
                
                # Prepare preview data
                preview_data = csv_data
                csv_data_json = json.dumps(csv_data)
                
                flash(f"CSV file validated successfully. {len(csv_data)} entries found.", "success")
                
            except Exception as e:
                flash(f"Error processing CSV file: {str(e)}", "danger")
                return redirect(url_for('fill_db'))
        
        return render_template('fill_db.html',
                              preview_data=preview_data,
                              selected_stage=selected_stage,
                              clear_existing=clear_existing,
                              csv_data_json=csv_data_json,
                              country_flags=country_flags)
    
    @app.route('/confirm-fill-db', methods=['POST'])
    def confirm_fill_db():
        if 'user_id' not in session:
            flash("You need to be logged in to access this page", "warning")
            return redirect(url_for('index'))
            
        # Verify user exists in database
        user_id = session['user_id']
        user = User.query.get(user_id)
        if not user:
            flash("Your session has expired. Please log in again.", "danger")
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('index'))
            
        # Get form data
        stage_id = request.form.get('stage')
        clear_existing = request.form.get('clear_existing') == 'True'
        csv_data_json = request.form.get('csv_data')
        
        if not csv_data_json:
            flash("No data provided", "danger")
            return redirect(url_for('fill_db'))
            
        try:
            # Parse JSON data
            csv_data = json.loads(csv_data_json)
            
            # Map stage_id to actual stage names
            stage_map = {
                'semi1': 'Semi-final 1',
                'semi2': 'Semi-final 2',
                'final': 'Final'
            }
            
            stage_name = stage_map.get(stage_id)
            
            if not stage_name:
                flash("Invalid stage selected", "danger")
                return redirect(url_for('fill_db'))
                
            # Get or create stage
            stage = Stage.query.filter_by(display_name=stage_name).first()
            if not stage:
                stage = Stage(display_name=stage_name)
                db.session.add(stage)
                db.session.commit()
                
            # Clear existing countries if requested
            if clear_existing:
                # Get all countries in this stage
                countries = Country.query.join(Stage.countries).filter(Stage.id == stage.id).all()
                
                # Remove countries from stage
                for country in countries:
                    stage.countries.remove(country)
                    
                db.session.commit()
                flash(f"Cleared existing countries from {stage_name}", "info")
            
            # Add countries from CSV
            countries_added = 0
            for row in csv_data:
                country_name = row['country'].strip()
                artist = row['artist'].strip()
                song = row['song'].strip()
                
                # Check if country already exists
                country = Country.query.filter_by(display_name=country_name).first()
                
                if not country:
                    # Create new country
                    country = Country(display_name=country_name, artist=artist, song=song)
                    db.session.add(country)
                else:
                    # Update existing country
                    country.artist = artist
                    country.song = song
                
                # Add country to stage if not already there
                if country not in stage.countries:
                    stage.countries.append(country)
                    countries_added += 1
            
            db.session.commit()
            flash(f"Successfully added {countries_added} countries to {stage_name}", "success")
            
            return redirect(url_for('stage', stage_id=stage.id))
            
        except Exception as e:
            flash(f"Error saving data to database: {str(e)}", "danger")
            return redirect(url_for('fill_db'))

    @app.route('/stage/<int:stage_id>/submit/<int:country_id>', methods=['POST'])
    def submit_grades(stage_id, country_id):
        if 'user_id' not in session:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': "Please log in to vote"})
            flash("Please log in to vote", "warning")
            return redirect(url_for('index'))

        user_id = session['user_id']
        
        # Verify user exists in database
        user = User.query.get(user_id)
        if not user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': "User not found. Please log in again."})
            flash("User not found. Please log in again.", "danger")
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('index'))
        # Convert grade_value to integer
        try:
            grade_value = int(request.form.get('grade'))
            # Validate grade is within allowed range
            if not 1 <= grade_value <= 12:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': "Grade must be between 1 and 12"})
                flash("Grade must be between 1 and 12", "danger")
                return redirect(url_for('stage', stage_id=stage_id))
        except (ValueError, TypeError):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': "Invalid grade value"})
            flash("Invalid grade value", "danger")
            return redirect(url_for('stage', stage_id=stage_id))

        # Always create a new grade with the current timestamp
        # This ensures we have a history of all votes and can get the latest one
        new_grade = Grade(
            user_id=user_id,
            stage_id=stage_id,
            country_id=country_id,
            value=grade_value,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_grade)

        db.session.commit()
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Get updated rankings for this stage
            rankings = db.session.query(
                Country.id,
                db.func.sum(Grade.value).label('total_grade')
            ).join(Grade).filter(Grade.stage_id == stage_id).group_by(Country.id).order_by(
                db.func.sum(Grade.value).desc()).all()
            
            # Format rankings for JSON response
            rankings_data = [{'country_id': country_id, 'total_grade': total_grade}
                            for country_id, total_grade in rankings]
            
            return jsonify({
                'success': True,
                'message': "Your vote has been recorded!",
                'rankings': rankings_data
            })
            
        flash("Your vote has been recorded!", "success")
        return redirect(url_for('stage', stage_id=stage_id))
        
    @app.route('/stage/<int:stage_id>/user/<int:user_id>')
    def user_votes(stage_id, user_id):
        if 'user_id' not in session:
            flash("Please log in to view user votes", "warning")
            return redirect(url_for('index'))
            
        # Verify current user exists in database
        current_user = User.query.get(session['user_id'])
        if not current_user:
            flash("Your session has expired. Please log in again.", "danger")
            session.pop('user_id', None)
            session.pop('username', None)
            return redirect(url_for('index'))
            
        stage = Stage.query.get_or_404(stage_id)
        
        # Verify requested user exists
        user = User.query.get(user_id)
        if not user:
            flash("The requested user does not exist.", "danger")
            return redirect(url_for('stage', stage_id=stage_id))
        
        # Get all grades for this user in this stage, ensuring no duplicates
        # Use distinct to get only the latest grade for each country
        latest_grades = db.session.query(
            Grade.country_id,
            db.func.max(Grade.timestamp).label('latest_timestamp')
        ).filter_by(
            user_id=user_id,
            stage_id=stage_id
        ).group_by(Grade.country_id).all()
        
        # Create a list of (country, grade) tuples
        user_grades = []
        for country_id, latest_timestamp in latest_grades:
            # Get the grade with the latest timestamp
            grade = Grade.query.filter_by(
                user_id=user_id,
                stage_id=stage_id,
                country_id=country_id,
                timestamp=latest_timestamp
            ).first()
            
            if grade:
                country = Country.query.get(grade.country_id)
                user_grades.append((country, grade.value))
            
        # Sort by grade value (highest first)
        user_grades.sort(key=lambda x: x[1], reverse=True)
        
        return render_template('user_votes.html',
                              user=user,
                              stage=stage,
                              user_grades=user_grades,
                              country_flags=country_flags)