import os

DEBUG_MODE = True
SECRET_KEY = 'secret'

# Database config
DB_USER = 'postgres'
DB_NAME = 'postgres'
DB_PASSWORD = ''
DB_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

# Slack config
SLACK_TOKEN = 'token'
SLACK_API_INVITE_URL = 'https://slack.com/api/users.admin.invite'

# Email config
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587

PROJECTOR_IP = ''
DOOR_ENDPOINT = ''
