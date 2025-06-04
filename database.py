
import json
from datetime import datetime

# In-memory storage for Vercel serverless compatibility
surveys_storage = {}

def init_database():
    """Initialize in-memory storage - no action needed for Vercel"""
    pass

def save_survey(survey_id, survey_data):
    """Save survey data to in-memory storage"""
    surveys_storage[survey_id] = {
        'survey_data': survey_data,
        'created_at': datetime.now().isoformat(),
        'submission_count': 0
    }

def get_survey(survey_id):
    """Get survey data from in-memory storage"""
    if survey_id in surveys_storage:
        return surveys_storage[survey_id]['survey_data']
    return None

def increment_submission_count(survey_id):
    """Increment submission count for a survey"""
    if survey_id in surveys_storage:
        surveys_storage[survey_id]['submission_count'] += 1

def get_all_surveys():
    """Get all surveys with their submission counts"""
    surveys = []
    for survey_id, data in surveys_storage.items():
        survey_data = data['survey_data'].copy()
        survey_data['submission_count'] = data['submission_count']
        survey_data['created_at'] = data['created_at']
        surveys.append(survey_data)
    
    # Sort by creation date (most recent first)
    surveys.sort(key=lambda x: x['created_at'], reverse=True)
    return surveys
