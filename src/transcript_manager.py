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

        self.start_times = []  # Changed to a list to maintain sorted order
        self.time_tolerance = 0.05 # Define what "too close" means (e.g., 0.1 seconds)

    def reset(self):
        """Reset the context and index tracking."""
        self.words.clear()
        self._global_index_offset = 0

    def add_word(self, word: TranscriptWord) -> int:
        """Add a word to the context and return its absolute index. Return -1 wen word not added"""
    
        idx = bisect.bisect_left(self.start_times, word.startTime)

        # 2. Check the existing timestamp immediately BEFORE the new one
        if idx > 0 and (word.startTime - self.start_times[idx - 1]) <= self.time_tolerance:
            return -1  # Too close to the previous word
            
        # 3. Check the existing timestamp immediately AFTER the new one
        if idx < len(self.start_times) and (self.start_times[idx] - word.startTime) <= self.time_tolerance:
            return -1  # Too close to the next word

        # 4. If it passes the checks, insert the time to keep the list sorted
        bisect.insort(self.start_times, word.startTime)
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