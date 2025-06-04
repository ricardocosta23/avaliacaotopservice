
import json
import os
from datetime import datetime

# In-memory storage for temporary data
surveys_storage = {}
submission_counts = {}

def init_database():
    """Initialize in-memory storage - no action needed for Vercel"""
    pass

def save_survey(survey_id, survey_data):
    """Save survey data to in-memory storage and environment variable for persistence"""
    surveys_storage[survey_id] = {
        'survey_data': survey_data,
        'created_at': datetime.now().isoformat(),
        'submission_count': 0
    }
    
    # Also save to environment variable for persistence across serverless restarts
    # Note: This is a simplified approach - in production you'd use a database
    env_key = f"SURVEY_{survey_id}"
    os.environ[env_key] = json.dumps(survey_data)

def get_survey(survey_id):
    """Get survey data from in-memory storage or environment variable"""
    # First check in-memory storage
    if survey_id in surveys_storage:
        return surveys_storage[survey_id]['survey_data']
    
    # If not in memory, check environment variable
    env_key = f"SURVEY_{survey_id}"
    survey_json = os.environ.get(env_key)
    if survey_json:
        try:
            survey_data = json.loads(survey_json)
            # Restore to in-memory storage
            surveys_storage[survey_id] = {
                'survey_data': survey_data,
                'created_at': datetime.now().isoformat(),
                'submission_count': submission_counts.get(survey_id, 0)
            }
            return survey_data
        except json.JSONDecodeError:
            pass
    
    return None

def increment_submission_count(survey_id):
    """Increment submission count for a survey"""
    if survey_id in surveys_storage:
        surveys_storage[survey_id]['submission_count'] += 1
    
    # Also track in persistent counter
    submission_counts[survey_id] = submission_counts.get(survey_id, 0) + 1

def get_all_surveys():
    """Get all surveys with their submission counts"""
    surveys = []
    
    # Get surveys from in-memory storage
    for survey_id, data in surveys_storage.items():
        survey_data = data['survey_data'].copy()
        survey_data['submission_count'] = data['submission_count']
        survey_data['created_at'] = data['created_at']
        surveys.append(survey_data)
    
    # Also check environment variables for surveys not in memory
    for key, value in os.environ.items():
        if key.startswith("SURVEY_"):
            survey_id = key.replace("SURVEY_", "")
            if survey_id not in surveys_storage:
                try:
                    survey_data = json.loads(value)
                    survey_data['submission_count'] = submission_counts.get(survey_id, 0)
                    survey_data['created_at'] = datetime.now().isoformat()
                    surveys.append(survey_data)
                except json.JSONDecodeError:
                    pass
    
    # Sort by creation date (most recent first)
    surveys.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return surveys
