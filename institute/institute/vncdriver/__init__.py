import logging

from institute.vncdriver.vnc_session import VNCSession
from institute.vncdriver.vnc_client import client_factory
from institute.vncdriver.screen import NumpyScreen, PygletScreen

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
