import bisect
from collections import deque
from threading import Lock
from src.types import TranscriptWord
from streamlit import session_state as st_session_state
import streamlit as st

st.cache_resource()
def return_manager():
    return TranscriptManager()

class TranscriptManager:
    _instance = None
    _lock = Lock()


    def __new__(cls):
        """Implement Singleton pattern to ensure one source of truth."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TranscriptManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.words = deque()
        self.start_times = []
        self._global_index_offset = 0
        self._initialized = True


    def reset(self):
        """Reset the context and index tracking."""
        self.words.clear()
        self._global_index_offset = 0

    def add_word(self, word: TranscriptWord) -> int:
        """Add a word to the context and return its absolute index. Return -1 wen word not added"""

        self.words.append(word)
        
        return len(self.words) - 1 + self._global_index_offset

    def get_words(self, start_index: int, end_index: int) -> list[TranscriptWord]:
        """
        Get words between the specified indices (inclusive of start, exclusive of end).
        Adjusts for the deque's internal indexing relative to the global stream.
        """
        # Calculate local indices relative to what's currently in the deque
        local_start = start_index - self._global_index_offset
        local_end = end_index - self._global_index_offset

        # Ensure indices are within bounds
        local_start = max(0, local_start)
        local_end = min(len(self.words), local_end)

        if local_start >= local_end:
            return []

        # Convert deque slice to list
        return list(self.words)[local_start:local_end]