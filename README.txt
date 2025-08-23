Credit Intelligence Dashboard
============================

A Flask-based web application for visualizing and analyzing credit scores of companies.

Features:
- Dashboard overview of company credit scores
- Detailed company views with historical trends
- Feature importance visualization
- News and events impact tracking

Setup Instructions:
1. Extract all files to a directory
2. Open terminal/command prompt in that directory
3. Create a virtual environment (optional but recommended):
   - python -m venv venv
   - venv\Scripts\activate (Windows) or source venv/bin/activate (macOS/Linux)
4. Install dependencies: pip install -r requirements.txt
5. Run the application: python app.py
6. Open browser to http://localhost:5000

Requirements:
- Python 3.6+
- Flask
- SQLite (included with Python)

The application will automatically create a SQLite database with sample data when first run.

venv\Scripts\activate
python app.py