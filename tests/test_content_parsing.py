from obyde.parsing import parse_content_blocks, ContentBlock, PreformattedContentBlock


def test_parse_no_prefromatted_blocks():
    content = """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an 
    unknown printer took a galley of type and scrambled it to make a type specimen book. 
    It has survived not only five centuries, but also the leap into electronic typesetting, 
    remaining essentially unchanged."""

    blocks = parse_content_blocks(content)
    assert len(blocks) == 1
    assert isinstance(blocks[0], ContentBlock)
    assert blocks[0].content == content

def test_parse_preformatted_block_at_end():
    plain_content = """Lorem Ipsum is simply dummy text of the printing and typesetting industry.
    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an 
    unknown printer took a galley of type and scrambled it to make a type specimen book. 
    It has survived not only five centuries, but also the leap into electronic typesetting, 
    remaining essentially unchanged.
    PREFORMATTED BLOCK:"""
    preformatted_content = "this is a preformatted block"
    content = f"{plain_content}```{preformatted_content}```"

    blocks = parse_content_blocks(content)
    assert len(blocks) == 2
    assert isinstance(blocks[0], ContentBlock)
    assert isinstance(blocks[1], PreformattedContentBlock)
    assert blocks[0].content == plain_content
    assert blocks[1].content == preformatted_content

def test_parse_inline_preformatted_block():
    plain_content_1 = "This is the start of the content."
    plain_content_2 = "Still on the same line."
    preformatted_content = "This is an in-line preformatted block"
    content = f"{plain_content_1}`{preformatted_content}`{plain_content_2}"
    blocks = parse_content_blocks(content)
    assert len(blocks) == 3
    assert isinstance(blocks[0], ContentBlock)
    assert isinstance(blocks[1], PreformattedContentBlock)
    assert isinstance(blocks[2], ContentBlock)
    assert blocks[0].content == plain_content_1
    assert blocks[1].content == preformatted_content
    assert blocks[2].content == plain_content_2

def test_parse_interleaved_preformatted_blocks():
    plain_content = [
        ContentBlock("This is a plain sentence."),
        ContentBlock("This is another plain sentence."),
        ContentBlock("Another plain block with [[an Obsidian link]]")
    ]
    preformatted_content = [
        PreformattedContentBlock("This is a preformatted block", wrapping_tick_count=1),
        PreformattedContentBlock("This is another preformatted block", wrapping_tick_count=2),
        PreformattedContentBlock("assert a == b and b == a", wrapping_tick_count=3)
    ]

    expected_content_blocks = [block for pair in zip(plain_content, preformatted_content) for block in pair]
    content = ""
    for block in expected_content_blocks:
        addition = block.content
        if isinstance(block, PreformattedContentBlock):
            ticks = "`" * block.wrapping_tick_count
            addition = f"{ticks}{block.content}{ticks}"
        content += addition

    blocks = parse_content_blocks(content)
    assert len(blocks) == len(expected_content_blocks)
    for block, expected in zip(blocks, expected_content_blocks):
        assert isinstance(block, type(expected))
        assert block.content == expected.content