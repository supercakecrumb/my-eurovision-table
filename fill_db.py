import random
from app import app, db
from app.models import Stage, Country

def add_stages():
    stages = ['Semi-final 1', 'Semi-final 2', 'Final']
    for stage_name in stages:
        if not Stage.query.filter_by(display_name=stage_name).first():
            stage = Stage(display_name=stage_name)
            db.session.add(stage)
    db.session.commit()

def add_countries():
    countries = [
        'Sweden', 'Norway', 'Denmark', 'Finland', 'Iceland',
        'Italy', 'Spain', 'Germany', 'France', 'Netherlands'
    ]
    for country_name in countries:
        if not Country.query.filter_by(display_name=country_name).first():
            country = Country(display_name=country_name, artist='Artist ' + country_name, song='Song ' + country_name)
            db.session.add(country)
    db.session.commit()

def assign_countries_to_stages():
    stages = Stage.query.all()
    countries = Country.query.all()
    for country in countries:
        # Assign each country to 1 or 2 stages randomly
        assigned_stages = random.sample(stages, k=random.randint(1, 2))
        for stage in assigned_stages:
            if country not in stage.countries:
                stage.countries.append(country)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        add_stages()
        add_countries()
        assign_countries_to_stages()
