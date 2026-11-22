"""Compatibility tests for the case conversions used by generators and templates."""

import pytest

from qsdl import casing


@pytest.mark.parametrize(
    ("word", "raw", "normalized", "pascal", "snake", "spinal", "capital", "sentence"),
    [
        ("", "", "", "", "", "", "", ""),
        (
            "helloWorld",
            "helloWorld",
            "helloWorld",
            "HelloWorld",
            "hello_world",
            "hello-world",
            "HelloWorld",
            "Hello world",
        ),
        (
            "HTTPResponse",
            "hTTPResponse",
            "hTTPResponse",
            "HTTPResponse",
            "h_t_t_p_response",
            "h-t-t-p-response",
            "HTTPResponse",
            "H t t p response",
        ),
        ("my_field", "myField", "myField", "MyField", "my_field", "my-field", "My_field", "My field"),
        ("foo-bar", "foar", "fooBar", "Foar", "foo_bar", "foo-bar", "Foo-bar", "Foo bar"),
        ("a b", "", "aB", "", "a_b", "a-b", "A b", "A b"),
        ("Foo.Bar", "foar", "foo_Bar", "Foar", "foo__bar", "foo--bar", "Foo.Bar", "Foo  bar"),
    ],
)
def test_case_conversions(
    word: str, raw: str, normalized: str, pascal: str, snake: str, spinal: str, capital: str, sentence: str
) -> None:
    assert casing.raw_camelcase(word) == raw
    assert casing.camelcase(word) == normalized
    assert casing.pascalcase(word) == pascal
    assert casing.snakecase(word) == snake
    assert casing.spinalcase(word) == spinal
    assert casing.capitalcase(word) == capital
    assert casing.sentencecase(word) == sentence
    assert casing.lowercase(word) == word.lower()
