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