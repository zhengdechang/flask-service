import logging
import os

class Flask_Logger:

    def __init__(self,
                 component_name,
                 logging_level=logging.DEBUG,
                 log_folder=''):
        self.log_folder = log_folder
        self.logger = logging.getLogger(f"{component_name}")
        self.logging_level = logging_level
        self.set_format(self.logging_level)

    def set_format(self, logging_level):
        formatter = logging.Formatter(
            f"[{self.logger.name}] %(asctime)s - %(levelname)s - [%(funcName)s] [%(lineno)d]: %(message)s"
        )
        handler = logging.StreamHandler()
        log_file_name = os.path.join(self.log_folder, f"flask_app.log")
        file_handler = logging.FileHandler(log_file_name)
        handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging_level)

    def get(self):
        return self.logger
