# Private Eurovision Voting Website

A web application for Eurovision Song Contest enthusiasts to vote for their favorite performances and view rankings.

## Overview

Private Eurovision Voting Website is a Flask-based web application that allows users to:
- Log in with a simple username
- Vote for Eurovision performances across different stages (Semi-finals and Final)
- View rankings based on all users' votes
- Track their own voting history

## Features

- **Simple Authentication**: Users can log in with just a username
- **Multiple Stages**: Support for Semi-final 1, Semi-final 2, and Final stages
- **Voting System**: Grade performances from 1-12 points (Eurovision style)
- **Real-time Rankings**: View current standings based on all votes
- **Responsive Design**: Bootstrap-based UI that works on various devices

## Technical Stack

- **Backend**: Python 3.12 with Flask framework
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, Bootstrap 5.1.3
- **Containerization**: Docker and Docker Compose for easy deployment

## Project Structure

```
private-eurovision-voting-website/
├── app/                      # Application package
│   ├── __init__.py           # Flask app initialization
│   ├── db_init.py            # Database initialization module
│   ├── forms.py              # WTForms definitions
│   ├── models.py             # SQLAlchemy database models
│   ├── routes.py             # Flask routes and view functions
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html         # Base template with common elements
│       ├── index.html        # Login and stage selection page
│       └── stage.html        # Voting and rankings page
├── data/                     # Local storage directory (for SQLite if used)
├── .env.example              # Example environment variables configuration
├── docker-compose.yml        # Docker Compose configuration with PostgreSQL
├── Dockerfile                # Docker container definition
├── fill_db.py                # Script to populate the database with initial data
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## Installation and Setup

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/supercakecrumb/private-eurovision-voting-website.git
   cd private-eurovision-voting-website
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up a PostgreSQL database or use SQLite for development:
   
   **Option 1: Use SQLite (easier for development)**
   ```
   mkdir data  # Create a data directory for the SQLite database
   ```
   
   **Option 2: Use PostgreSQL (recommended for production-like environment)**
   ```
   # Install PostgreSQL on your system
   # Create a database named 'eurovision'
   # Set the DATABASE_URL environment variable to point to your PostgreSQL database
   ```

4. Create a `.env` file with your configuration:
   ```
   # Database connection (use one of these)
   # For SQLite:
   DATABASE_URL=sqlite:///data/my-eurovision-table.db
   # For PostgreSQL:
   # DATABASE_URL=postgresql://username:password@localhost:5432/eurovision
   
   # Auto-initialization
   AUTO_INIT_DB=1
   USE_REAL_EUROVISION_DATA=1
   
   # Security
   SECRET_KEY=your_development_secret_key
   ```

5. Run the application:
   ```
   flask run
   ```
   
   The application will automatically initialize the database if `AUTO_INIT_DB=1` is set.
   
   Alternatively, you can manually initialize the database:
   ```
   python fill_db.py
   ```

6. Access the application at http://localhost:5000

### Docker Deployment

1. Clone the repository:
   ```
   git clone https://github.com/supercakecrumb/private-eurovision-voting-website.git
   cd private-eurovision-voting-website
   ```

2. (Optional) Create a `.env` file to override environment variables:
   ```
   # Database connection
   DATABASE_URL=postgresql://postgres:postgres@db:5432/eurovision
   
   # Auto-initialization
   AUTO_INIT_DB=1
   USE_REAL_EUROVISION_DATA=1
   
   # Security
   SECRET_KEY=your_secure_secret_key_here
   ```

3. Build and run using Docker Compose:
   ```
   docker-compose up -d
   ```

4. Access the application at http://localhost:5024

The application will automatically:
- Set up a PostgreSQL database
- Initialize the database with Eurovision data (if `AUTO_INIT_DB=1` is set)
- Use real Eurovision 2023 data (if `USE_REAL_EUROVISION_DATA=1` is set)

#### Database Persistence

PostgreSQL data is stored in a Docker volume (`postgres_data`), ensuring your data persists across container restarts.

## Usage

1. Log in with your username on the homepage
2. Select a stage (Semi-final 1, Semi-final 2, or Final)
3. Vote for each country's performance by assigning points (1-12)
4. View the current rankings in the Rankings tab

## Recent Improvements

### Bug Fixes

1. **Contestant Ordering**: Countries are now sorted by their total score in both the voting and rankings tabs.
2. **Routing Fix**: Corrected redirects to non-existent 'login' route to properly redirect to 'index'.
3. **Type Conversion**: Added proper type conversion and validation for grade values.
4. **Security Enhancement**: Replaced hardcoded secret key with environment variable and secure random fallback.
5. **Flash Messages**: Added flash message display to the base template for better user feedback.
6. **Code Cleanup**: Fixed duplicate import in fill_db.py.

### UI Enhancements

1. **Modern Design**: Implemented a modern, Eurovision-themed design with custom colors and styling.
2. **Responsive Layout**: Improved responsive layout for better mobile experience.
3. **Visual Hierarchy**: Enhanced visual hierarchy with cards, shadows, and spacing.
4. **Interactive Elements**: Added hover effects and transitions for a more interactive feel.
5. **Icons**: Integrated Font Awesome icons throughout the interface for visual cues.
6. **Rankings Visualization**: Added special styling for top 3 ranked countries with crown, award, and medal icons.
7. **Improved Navigation**: Enhanced navigation with back buttons and clearer tab interfaces.

### Data Enhancements

1. **Real Eurovision Data**: Added support for real Eurovision 2023 data through an environment variable (`USE_REAL_EUROVISION_DATA=1`).
2. **Auto-Initialization**: Added automatic database initialization with the `AUTO_INIT_DB=1` environment variable.
3. **Docker Integration**: Integrated environment variables in docker-compose.yml for easy deployment with real data.
4. **Testing Mode**: Implemented a testing mode with comprehensive data from previous Eurovision contests.
5. **Improved Feedback**: Enhanced console output during database initialization for better visibility.

## Remaining Limitations

- **Authentication**: The login system is very basic with no password protection.
- **Data Persistence**: The SQLite database is stored in a Docker volume. For production, consider using a more robust database solution.
- **Form Validation**: The grade input validation in the form (0-12) doesn't match the HTML input (1-12).

## Future Improvements

- Add proper user authentication with passwords
- Implement user profiles with voting history
- Add admin interface for managing stages and countries
- Implement real-time updates using WebSockets
- Add more detailed statistics and visualizations
- Improve error handling and user feedback

## License

© 2024 Aurorass. All rights reserved.