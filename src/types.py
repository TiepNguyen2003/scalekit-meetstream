from dataclasses import dataclass
from datetime import datetime
from typing import List
@dataclass(frozen=True)
class QueryCard():
    '''
    Returns summary + link of information
    '''
    title : str
    summary : List[str]
    link: str

@dataclass(frozen=True)
class TranscriptWord():
    '''
    Represents a single word in the context stream
    '''
    speakerName: str
    timestamp: datetime
    word : str
    speakerConfidence : float
    startTime : float
    endTime : float
    is_final : bool
    
    def to_dict(self) -> dict:
        return {
            "speakerName": self.speakerName,
            # Convert datetime to a JSON-serializable string format
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "word": self.word,
            "speakerConfidence": self.speakerConfidence,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "is_final": self.is_final
        }
