import sqlite3
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ticker TEXT,
            sector TEXT,
            current_score INTEGER
        )
    ''')
    
    # Create historical scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            date TEXT,
            score INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Create news table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            headline TEXT,
            sentiment TEXT,
            date TEXT,
            impact INTEGER,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Create features table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            name TEXT,
            value REAL,
            importance REAL,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM companies")
    if cursor.fetchone()[0] == 0:
        # Add sample companies
        companies = [
            ('Apple Inc.', 'AAPL', 'Technology', 85),
            ('Microsoft Corp.', 'MSFT', 'Technology', 88),
            ('Tesla Inc.', 'TSLA', 'Automotive', 72),
            ('Amazon.com Inc.', 'AMZN', 'Retail', 84),
            ('JPMorgan Chase & Co.', 'JPM', 'Financial', 79)
        ]
        
        cursor.executemany(
            "INSERT INTO companies (name, ticker, sector, current_score) VALUES (?, ?, ?, ?)",
            companies
        )
        
        # Add historical data for each company
        for company_id in range(1, 6):
            base_score = random.randint(70, 90)
            for days_ago in range(30, 0, -1):
                date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                score_variation = random.randint(-5, 5)
                score = max(1, min(100, base_score + score_variation))
                
                cursor.execute(
                    "INSERT INTO historical_scores (company_id, date, score) VALUES (?, ?, ?)",
                    (company_id, date, score)
                )
        
        # Add sample features
        feature_names = ['P/E Ratio', 'Volatility', 'Debt-to-Equity', 'Revenue Growth', 'Profit Margin', 'News Sentiment']
        for company_id in range(1, 6):
            for feature in feature_names:
                value = round(random.uniform(0, 1), 2)
                importance = round(random.uniform(0.05, 0.3), 2)
                
                cursor.execute(
                    "INSERT INTO features (company_id, name, value, importance) VALUES (?, ?, ?, ?)",
                    (company_id, feature, value, importance)
                )
        
        # Add sample news
        news_items = [
            (1, 'Apple announces record quarterly earnings', 'positive', 5),
            (1, 'New iPhone sales exceed expectations', 'positive', 4),
            (1, 'Supply chain issues may affect production', 'negative', -3),
            (2, 'Microsoft Azure continues strong growth', 'positive', 4),
            (2, 'New security vulnerabilities discovered', 'negative', -2),
            (3, 'Tesla recalls vehicles for software update', 'negative', -4),
            (3, 'New factory opening ahead of schedule', 'positive', 3),
            (4, 'Amazon expands logistics network', 'positive', 3),
            (4, 'Labor disputes affecting operations', 'negative', -3),
            (5, 'JPMorgan increases dividend', 'positive', 4),
            (5, 'Regulatory scrutiny increases', 'negative', -4)
        ]
        
        for company_id, headline, sentiment, impact in news_items:
            days_ago = random.randint(0, 7)
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            cursor.execute(
                "INSERT INTO news (company_id, headline, sentiment, date, impact) VALUES (?, ?, ?, ?, ?)",
                (company_id, headline, sentiment, date, impact)
            )
    
    # Create a demo user if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('demo123')
        cursor.execute(
            "INSERT INTO users (name, email, password, created_at) VALUES (?, ?, ?, ?)",
            ('Demo User', 'demo@example.com', hashed_password, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
    
    conn.commit()
    conn.close()

def get_companies():
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies")
    companies = cursor.fetchall()
    conn.close()
    return companies

def get_company_data(company_id):
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    company = cursor.fetchone()
    conn.close()
    return company

def get_news(company_id, limit=5):
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM news WHERE company_id = ? ORDER BY date DESC LIMIT ?", 
        (company_id, limit)
    )
    news = cursor.fetchall()
    conn.close()
    return news