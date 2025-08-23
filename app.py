from flask import Flask, render_template, jsonify, request, abort, session, redirect, url_for
from database import init_db, get_companies, get_company_data, get_news
from data_processor import calculate_score, get_feature_importance
import sqlite3
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Initialize database
init_db()

# Authentication required for all routes except login/signup
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'static']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))

@app.route('/')
def index():
    companies = get_companies()
    return render_template('index.html', companies=companies, now=datetime.now())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('credit_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, name FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['user_name'] = user[2]  # Store username in session
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        conn = sqlite3.connect('credit_data.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            conn.commit()
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['user_name'] = name  # Store username in session
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error='Email already exists')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('login'))

@app.route('/company/<int:company_id>')
def company_detail(company_id):
    company = get_company_data(company_id)
    news = get_news(company_id)
    return render_template('company.html', company=company, news=news)

@app.route('/companies')
def companies():
    companies = get_companies()
    return render_template('companies.html', companies=companies, now=datetime.now())

@app.route('/trends')
def trends():
    # Get some sample data for trends
    sectors = ['Technology', 'Financial', 'Retail', 'Automotive', 'Healthcare']
    avg_scores = [86, 79, 84, 72, 81]
    return render_template('trends.html', sectors=sectors, avg_scores=avg_scores)

@app.route('/accuracy')
def accuracy():
    # Basic sample data for the accuracy page
    data_info = {
        'num_samples': 10000,
        'num_features': 25,
        'feature_names': ['P/E Ratio', 'Volatility', 'Debt-to-Equity', 'Revenue Growth', 'Profit Margin', 
                         'News Sentiment', 'Feature7', 'Feature8', 'Feature9', 'Feature10', 
                         'Feature11', 'Feature12', 'Feature13', 'Feature14', 'Feature15', 
                         'Feature16', 'Feature17', 'Feature18', 'Feature19', 'Feature20', 
                         'Feature21', 'Feature22', 'Feature23', 'Feature24', 'Feature25'],
        'target_distribution': {'High Risk': 3000, 'Medium Risk': 4000, 'Low Risk': 3000}
    }

    # Sample model metrics
    model_metrics = {
        'overall_accuracy': 0.87,
        'precision': 0.85,
        'recall': 0.89,
        'f1_score': 0.87,
        'training_history': {
            'epochs': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'accuracy': [0.65, 0.72, 0.78, 0.82, 0.84, 0.85, 0.86, 0.86, 0.87, 0.87],
            'val_accuracy': [0.63, 0.70, 0.76, 0.80, 0.82, 0.83, 0.84, 0.84, 0.85, 0.85],
            'loss': [0.8, 0.6, 0.45, 0.35, 0.28, 0.23, 0.19, 0.16, 0.14, 0.12],
            'val_loss': [0.82, 0.62, 0.47, 0.37, 0.30, 0.25, 0.21, 0.18, 0.16, 0.14]
        },
        'feature_importance': {
            'features': ['P/E Ratio', 'Volatility', 'Debt-to-Equity', 'Revenue Growth', 'News Sentiment'],
            'importance': [0.25, 0.18, 0.22, 0.20, 0.15]
        },
        'confusion_matrix': {
            'labels': ['High Risk', 'Medium Risk', 'Low Risk'],
            'data': [[120, 15, 5], [10, 95, 15], [5, 10, 125]]
        }
    }
    
    return render_template('accuracy.html', 
                         data_info=data_info,
                         model_metrics=model_metrics,
                         now=datetime.now())

@app.route('/settings')
def settings():
    return render_template('settings.html', now=datetime.now())

@app.route('/api/scores/<int:company_id>')
def api_scores(company_id):
    # Get the days parameter from the request, default to 30
    days = request.args.get('days', 30, type=int)
    
    # Calculate the date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Get historical scores for chart
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, score FROM historical_scores 
        WHERE company_id = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
    ''', (company_id, start_date_str, end_date_str))
    
    scores = cursor.fetchall()
    conn.close()
    
    # Format for chart
    dates = [row[0] for row in scores]
    values = [row[1] for row in scores]
    
    return jsonify({
        'dates': dates,
        'scores': values
    })

@app.route('/api/feature_importance/<int:company_id>')
def api_feature_importance(company_id):
    importance = get_feature_importance(company_id)
    return jsonify(importance)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/<path:path>')
def catch_all(path):
    abort(404)

if __name__ == '__main__':
    app.run(debug=True)