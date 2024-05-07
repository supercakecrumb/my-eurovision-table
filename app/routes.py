from flask import render_template, request, redirect, session, url_for, flash
from .models import db, User, Stage, Country
from .forms import LoginForm

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
            return redirect(url_for('index'))
        stage = Stage.query.get_or_404(stage_id)
        countries = Country.query.join(Stage.countries).filter(Stage.id == stage_id).all()
        return render_template('stage.html', stage=stage, countries=countries)
