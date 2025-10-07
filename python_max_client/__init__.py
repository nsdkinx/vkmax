"""
python-max-client
Python client library for VK MAX messenger (OneMe)
"""

__version__ = "1.0.0"
__author__ = "huxuxuya"
__email__ = "huxuxuya@gmail.com"

from .client import MaxClient
from .packet import Packet

__all__ = ["MaxClient", "Packet"]
