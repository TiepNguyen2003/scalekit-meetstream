from dataclasses import dataclass
from typing import List
@dataclass(frozen=True)
class QueryCard():
    '''
    Returns summary + link of information
    '''
    title : str
    summary : List[str]
    link: str
