"""Backend package for Friday Assistant"""

__version__ = "2.0.0"
__author__ = "Friday Assistant Team"

from .brain import GeminiBrain
from .logger import Logger
from .memory_handler import MemoryHandler
from .llm_handler import LLMHandler

__all__ = ["GeminiBrain", "Logger", "MemoryHandler", "LLMHandler"]