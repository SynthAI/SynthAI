import logging
from lab import configuration

institute_logger = logging.getLogger('institute')
institute_logger.setLevel(logging.INFO)

extra_logger = logging.getLogger('institute.extra')
extra_logger.setLevel(logging.INFO)

if hasattr(configuration, '_extra_loggers'):
    configuration._extra_loggers.append(institute_logger)
    configuration._extra_loggers.append(extra_logger)
