def test_markitdown_importable():
    import markitdown

    assert hasattr(markitdown, "MarkItDown")
