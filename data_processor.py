import sqlite3

def calculate_score(company_id):
    # This is a simplified scoring function
    # In a real application, this would use more sophisticated algorithms
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    
    # Get feature values and importance
    cursor.execute("SELECT value, importance FROM features WHERE company_id = ?", (company_id,))
    features = cursor.fetchall()
    
    # Calculate weighted score (simplified)
    base_score = 50
    for value, importance in features:
        base_score += value * importance * 100
    
    # Ensure score is between 1 and 100
    score = max(1, min(100, base_score))
    
    conn.close()
    return round(score)

def get_feature_importance(company_id):
    # Get feature importance data
    conn = sqlite3.connect('credit_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, importance FROM features WHERE company_id = ?", (company_id,))
    features = cursor.fetchall()
    conn.close()
    
    # Format for response
    result = {
        'labels': [f[0] for f in features],
        'values': [f[1] for f in features]
    }
    
    return result