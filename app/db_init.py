import random
import os
from .models import db, Stage, Country, StageCountry

# Check for environment variable to use real Eurovision data
# Set USE_REAL_EUROVISION_DATA=1 to use real data from previous contests
# This is for testing purposes only
USE_REAL_DATA = os.getenv('USE_REAL_EUROVISION_DATA', '0') == '1'

# Real Eurovision 2023 data for testing purposes
EUROVISION_2023_DATA = {
    'Semi-final 1': [
        {'country': 'Finland', 'artist': 'Käärijä', 'song': 'Cha Cha Cha'},
        {'country': 'Sweden', 'artist': 'Loreen', 'song': 'Tattoo'},
        {'country': 'Israel', 'artist': 'Noa Kirel', 'song': 'Unicorn'},
        {'country': 'Czech Republic', 'artist': 'Vesna', 'song': 'My Sister\'s Crown'},
        {'country': 'Moldova', 'artist': 'Pasha Parfeni', 'song': 'Soarele și Luna'},
        {'country': 'Norway', 'artist': 'Alessandra', 'song': 'Queen of Kings'},
        {'country': 'Croatia', 'artist': 'Let 3', 'song': 'Mama ŠČ!'},
        {'country': 'Switzerland', 'artist': 'Remo Forrer', 'song': 'Watergun'},
        {'country': 'Portugal', 'artist': 'Mimicat', 'song': 'Ai Coração'},
        {'country': 'Serbia', 'artist': 'Luke Black', 'song': 'Samo Mi Se Spava'},
        {'country': 'Latvia', 'artist': 'Sudden Lights', 'song': 'Aijā'},
        {'country': 'Ireland', 'artist': 'Wild Youth', 'song': 'We Are One'},
        {'country': 'Netherlands', 'artist': 'Mia Nicolai & Dion Cooper', 'song': 'Burning Daylight'},
        {'country': 'Azerbaijan', 'artist': 'TuralTuranX', 'song': 'Tell Me More'},
        {'country': 'Malta', 'artist': 'The Busker', 'song': 'Dance (Our Own Party)'},
    ],
    'Semi-final 2': [
        {'country': 'Albania', 'artist': 'Albina & Familja Kelmendi', 'song': 'Duje'},
        {'country': 'Cyprus', 'artist': 'Andrew Lambrou', 'song': 'Break a Broken Heart'},
        {'country': 'Romania', 'artist': 'Theodor Andrei', 'song': 'D.G.T. (Off and On)'},
        {'country': 'Denmark', 'artist': 'Reiley', 'song': 'Breaking My Heart'},
        {'country': 'Belgium', 'artist': 'Gustaph', 'song': 'Because of You'},
        {'country': 'Iceland', 'artist': 'Diljá', 'song': 'Power'},
        {'country': 'Greece', 'artist': 'Victor Vernicos', 'song': 'What They Say'},
        {'country': 'Estonia', 'artist': 'Alika', 'song': 'Bridges'},
        {'country': 'Australia', 'artist': 'Voyager', 'song': 'Promise'},
        {'country': 'Austria', 'artist': 'Teya & Salena', 'song': 'Who The Hell Is Edgar?'},
        {'country': 'Lithuania', 'artist': 'Monika Linkytė', 'song': 'Stay'},
        {'country': 'San Marino', 'artist': 'Piqued Jacks', 'song': 'Like An Animal'},
        {'country': 'Slovenia', 'artist': 'Joker Out', 'song': 'Carpe Diem'},
        {'country': 'Georgia', 'artist': 'Iru', 'song': 'Echo'},
        {'country': 'Armenia', 'artist': 'Brunette', 'song': 'Future Lover'},
    ],
    'Final': [
        {'country': 'Sweden', 'artist': 'Loreen', 'song': 'Tattoo'},
        {'country': 'Finland', 'artist': 'Käärijä', 'song': 'Cha Cha Cha'},
        {'country': 'Israel', 'artist': 'Noa Kirel', 'song': 'Unicorn'},
        {'country': 'Italy', 'artist': 'Marco Mengoni', 'song': 'Due Vite'},
        {'country': 'Norway', 'artist': 'Alessandra', 'song': 'Queen of Kings'},
        {'country': 'Ukraine', 'artist': 'TVORCHI', 'song': 'Heart of Steel'},
        {'country': 'Belgium', 'artist': 'Gustaph', 'song': 'Because of You'},
        {'country': 'Estonia', 'artist': 'Alika', 'song': 'Bridges'},
        {'country': 'Australia', 'artist': 'Voyager', 'song': 'Promise'},
        {'country': 'Czech Republic', 'artist': 'Vesna', 'song': 'My Sister\'s Crown'},
        {'country': 'Lithuania', 'artist': 'Monika Linkytė', 'song': 'Stay'},
        {'country': 'Cyprus', 'artist': 'Andrew Lambrou', 'song': 'Break a Broken Heart'},
        {'country': 'Croatia', 'artist': 'Let 3', 'song': 'Mama ŠČ!'},
        {'country': 'Armenia', 'artist': 'Brunette', 'song': 'Future Lover'},
        {'country': 'Austria', 'artist': 'Teya & Salena', 'song': 'Who The Hell Is Edgar?'},
        {'country': 'Switzerland', 'artist': 'Remo Forrer', 'song': 'Watergun'},
        {'country': 'France', 'artist': 'La Zarra', 'song': 'Évidemment'},
        {'country': 'Spain', 'artist': 'Blanca Paloma', 'song': 'Eaea'},
        {'country': 'Moldova', 'artist': 'Pasha Parfeni', 'song': 'Soarele și Luna'},
        {'country': 'Poland', 'artist': 'Blanka', 'song': 'Solo'},
        {'country': 'Portugal', 'artist': 'Mimicat', 'song': 'Ai Coração'},
        {'country': 'Serbia', 'artist': 'Luke Black', 'song': 'Samo Mi Se Spava'},
        {'country': 'United Kingdom', 'artist': 'Mae Muller', 'song': 'I Wrote A Song'},
        {'country': 'Slovenia', 'artist': 'Joker Out', 'song': 'Carpe Diem'},
        {'country': 'Albania', 'artist': 'Albina & Familja Kelmendi', 'song': 'Duje'},
        {'country': 'Germany', 'artist': 'Lord Of The Lost', 'song': 'Blood & Glitter'},
    ]
}

# Dummy data for when real data is not used
DUMMY_DATA = {
    'stages': ['Semi-final 1', 'Semi-final 2', 'Final'],
    'countries': [
        'Sweden', 'Norway', 'Denmark', 'Finland', 'Iceland',
        'Italy', 'Spain', 'Germany', 'France', 'Netherlands'
    ]
}

def add_stages():
    """Add Eurovision stages to the database"""
    stages = DUMMY_DATA['stages']
    for stage_name in stages:
        if not Stage.query.filter_by(display_name=stage_name).first():
            stage = Stage(display_name=stage_name)
            db.session.add(stage)
    db.session.commit()
    print("✅ Stages added successfully")

def add_countries():
    """Add countries to the database - uses real Eurovision data if enabled"""
    if USE_REAL_DATA:
        # Collect all unique countries from all stages
        all_countries = set()
        for stage, entries in EUROVISION_2023_DATA.items():
            for entry in entries:
                all_countries.add((entry['country'], entry['artist'], entry['song']))
        
        # Add each unique country to the database
        for country_name, artist, song in all_countries:
            if not Country.query.filter_by(display_name=country_name).first():
                country = Country(display_name=country_name, artist=artist, song=song)
                db.session.add(country)
        
        print(f"✅ Added {len(all_countries)} countries with real Eurovision 2023 data")
    else:
        # Use dummy data
        for country_name in DUMMY_DATA['countries']:
            if not Country.query.filter_by(display_name=country_name).first():
                country = Country(display_name=country_name, artist='Artist ' + country_name, song='Song ' + country_name)
                db.session.add(country)
        print(f"✅ Added {len(DUMMY_DATA['countries'])} countries with dummy data")
    
    db.session.commit()

def assign_countries_to_stages():
    """Assign countries to stages - uses real Eurovision data if enabled"""
    # Clear existing assignments
    StageCountry.query.delete()
    db.session.commit()
    
    if USE_REAL_DATA:
        # Assign countries according to real Eurovision 2023 data
        for stage_name, entries in EUROVISION_2023_DATA.items():
            stage = Stage.query.filter_by(display_name=stage_name).first()
            if not stage:
                continue
                
            # Add countries with their performance order
            for order, entry in enumerate(entries, 1):
                country = Country.query.filter_by(display_name=entry['country']).first()
                if country:
                    # Create association with order
                    stage_country = StageCountry(
                        stage_id=stage.id,
                        country_id=country.id,
                        order=order
                    )
                    db.session.add(stage_country)
        
        print(f"✅ Assigned countries to stages with order using real Eurovision 2023 data")
    else:
        # Use random assignment for dummy data
        stages = Stage.query.all()
        countries = Country.query.all()
        for country in countries:
            # Assign each country to 1 or 2 stages randomly
            assigned_stages = random.sample(stages, k=random.randint(1, 2))
            for stage in assigned_stages:
                # Get the next available order number for this stage
                max_order = db.session.query(db.func.max(StageCountry.order)).filter_by(stage_id=stage.id).scalar() or 0
                
                # Create association with order
                stage_country = StageCountry(
                    stage_id=stage.id,
                    country_id=country.id,
                    order=max_order + 1
                )
                db.session.add(stage_country)
        
        print(f"✅ Randomly assigned countries to stages with order")
    
    db.session.commit()

def initialize_database():
    """Initialize the database with stages, countries, and assignments"""
    print("\n🎵 Eurovision Table Database Setup 🎵")
    print("=====================================")
    
    if USE_REAL_DATA:
        print("✨ Using REAL Eurovision 2023 data (from environment variable USE_REAL_EUROVISION_DATA=1)")
        print("✨ This is for testing purposes only")
    else:
        print("✨ Using dummy data (set USE_REAL_EUROVISION_DATA=1 to use real Eurovision data)")
    
    print("=====================================\n")
    
    add_stages()
    add_countries()
    assign_countries_to_stages()
    
    # Count entries for verification
    stages_count = Stage.query.count()
    countries_count = Country.query.count()
    
    print("\n✅ Database setup complete!")
    print(f"✅ Added {stages_count} stages")
    print(f"✅ Added {countries_count} countries")
    
    # Count stage-country associations
    associations_count = StageCountry.query.count()
    print(f"✅ Created {associations_count} stage-country associations with order")