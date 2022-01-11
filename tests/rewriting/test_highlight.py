from obyde.rewriting.highlight import ObsidianHighlightRewritingTransformer

def test_highlight_does_not_modify_preformatted_blocks():
    preformatted = "if a == b and b == c:\n\tpass"
    highlighter = ObsidianHighlightRewritingTransformer()
    highlighted = highlighter.transform_preformatted_block(preformatted)
    assert highlighted is None

def test_highlight_does_not_modify_metadata_blocks():
    metadata = '---\ndate: 2021-08-21\ntitle: "== title =="'
    highlighter = ObsidianHighlightRewritingTransformer()
    highlighted = highlighter.transform_preformatted_block(metadata)
    assert highlighted is None

def test_highlight_does_not_modify_content_blocks_with_no_highlights():
    content = "This is a normal content block with no highlighted text."
    highlighter = ObsidianHighlightRewritingTransformer()
    highlighted = highlighter.transform_normal_block(content)
    assert highlighted is None

def test_highlight_markup_content_block():
    content = "This is a normal content block with ==highlighted text==."
    expected = "This is a normal content block with <mark>highlighted text</mark>."
    highlighter = ObsidianHighlightRewritingTransformer()
    highlighted = highlighter.transform_normal_block(content)
    assert highlighted == expected

def test_highlight_content_spans_new_lines():
    content = "This is a content block with ==highlighted text\nspanning multiple lines=="
    expected = "This is a content block with <mark>highlighted text\nspanning multiple lines</mark>"
    highlighter = ObsidianHighlightRewritingTransformer()
    highlighted = highlighter.transform_normal_block(content)
    assert highlighted == expected