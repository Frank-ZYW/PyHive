from os import getenv, getcwd


# workspace
APP_DEBUG = bool(getenv('APP_DEBUG', False))
WORKPLACE = getenv('WORKPLACE', getcwd())
LOG_DIR = 'logs'
PROJECTS_DIR = 'projects'
DB_DIR = 'dbs'

# scheduler
SCHEDULER_HEARTBEAT = 1  # min
