"""Tests for filename sanitization logic."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.autosave import AutoSave


class TestSanitizeFilename:

    OS_ILLEGAL_CASES = [
        (r"test\file",    "testfile"),
        (r"**\\wode",     "wode"),
        ("hello:world",   "helloworld"),
        ('test"file',     "testfile"),
        ("a<b>c",         "abc"),
        ("one/two",       "onetwo"),
        ("file|name",     "filename"),
        ("test?file",     "testfile"),
        ("test*file",     "testfile"),
    ]

    MD_FORMAT_CASES = [
        ("**bold**",      "bold"),
        ("*italic*",      "italic"),
        ("~~strike~~",    "strike"),
        ("__underline__", "underline"),
        ("`code`",        "code"),
        ("[link](url)",   "linkurl"),
        ("### Heading",   "Heading"),
    ]

    MIXED_CASES = [
        (r"**\\测试**",   "测试"),
        ("**[链接](url)**", "链接url"),
    ]

    EDGE_CASES = [
        ("",              "未命名"),
        ("***___~~~",     "未命名"),
        ("_" * 50,        "未命名"),
        ("a" * 50,        "a" * 40),
        ("   spaced   ",  "spaced"),
        ("你好世界",      "你好世界"),
    ]

    @pytest.mark.parametrize("input_name, expected", [
        *OS_ILLEGAL_CASES,
        *MD_FORMAT_CASES,
        *MIXED_CASES,
        *EDGE_CASES,
    ])
    def test_sanitize_filename(self, input_name, expected):
        assert AutoSave._sanitize_filename(input_name) == expected
