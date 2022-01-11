from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class ContentBlock:
    content: str

@dataclass(frozen=True)
class PreformattedContentBlock(ContentBlock):
    wrapping_tick_count: int

def parse_content_blocks(content: str) -> List[ContentBlock]:
    pass