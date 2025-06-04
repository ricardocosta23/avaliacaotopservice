
import sqlite3
import json
import os
from datetime import datetime

DATABASE_PATH = 'surveys.db'

def init_database():
    """Initialize the database with surveys table"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS surveys (
            survey_id TEXT PRIMARY KEY,
            survey_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submission_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def save_survey(survey_id, survey_data):
    """Save survey data to database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO surveys (survey_id, survey_data, created_at)
        VALUES (?, ?, ?)
    ''', (survey_id, json.dumps(survey_data), datetime.now()))
    
    conn.commit()
    conn.close()

def get_survey(survey_id):
    """Get survey data from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT survey_data FROM surveys WHERE survey_id = ?', (survey_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def increment_submission_count(survey_id):
    """Increment submission count for a survey"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE surveys 
        SET submission_count = submission_count + 1 
        WHERE survey_id = ?
    ''', (survey_id,))
    
    conn.commit()
    conn.close()

def get_all_surveys():
    """Get all surveys with their submission counts"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT survey_id, survey_data, created_at, submission_count 
        FROM surveys 
        ORDER BY created_at DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    surveys = []
    for row in results:
        survey_data = json.loads(row[1])
        survey_data['submission_count'] = row[3]
        survey_data['created_at'] = row[2]
        surveys.append(survey_data)
    
    return surveys
