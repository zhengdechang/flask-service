import os
import logging as logging_alia
from log.flask_logger import Flask_Logger

log_folder = os.environ.get('LOG_FOLDER', './')

logging = Flask_Logger('flask_app',
                       logging_level=logging_alia.INFO,
                       log_folder=log_folder).get()
