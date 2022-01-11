from dataclasses import dataclass
from typing import List
from io import StringIO


@dataclass(frozen=True)
class ContentBlock:
    content: str


@dataclass(frozen=True)
class PreformattedContentBlock(ContentBlock):
    wrapping_tick_count: int


def parse_content_blocks(content: str) -> List[ContentBlock]:
    blocks = []
    state = 'open'
    quotemult = 0
    idx = 0
    buffer = StringIO()

    while idx < len(content):
        c = content[idx]
        incr = 1
        if c == '`':
            if state == 'open':
                tick_mult = _substr_cond(content, idx, lambda _, y: y == '`')
                quotemult = len(tick_mult)
                state = 'codestart'
                incr = quotemult
                if buffer.tell() > 0:
                    blocks.append(ContentBlock(content=buffer.getvalue()))
                    buffer = StringIO()
            elif state == 'code':
                tick_mult = _substr_cond(content, idx, lambda _, y: y == '`')
                ltick = len(tick_mult)
                # If the number of ticks in a row is equal to or larger than the initial
                # number of ticks. Assume that the open block is now closed
                # with the initial number of ticks, and if there are any
                # more ticks remaining, they will get handled in the next
                # loop iteration.
                incr = ltick if ltick < quotemult else quotemult
                if incr >= quotemult:
                    state = 'open'
                    # Preformatted content blocks can never be empty
                    # this would otherwise be an unterminated block
                    blocks.append(PreformattedContentBlock(
                        content=buffer.getvalue(), wrapping_tick_count=quotemult))
                    buffer = StringIO()
                    quotemult = 0
                else:
                    buffer.write(c)
        else:
            if state == 'codestart':
                state = 'code'
            buffer.write(c)

        idx += incr

    if state == 'code' or state == 'codestart':
            raise ValueError('Unterminated preformatted content block.')

    final_block = buffer.getvalue()
    if final_block:
        blocks.append(ContentBlock(content=final_block))
    return blocks


def _substr_cond(s, idx, cond):
    res = ''
    count = 0
    if idx < 0:
        raise ValueError('Invalid index')
    if not cond:
        raise ValueError('Condition must be provided')
    while (idx + count) < len(s):
        c = s[idx + count]
        if cond(count, c):
            res += c
        else:
            break
        count += 1
    return res
