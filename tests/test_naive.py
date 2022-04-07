import spacy
nlp = spacy.load("en_core_web_sm")
from pattern.text.en import singularize, pluralize

def test_naive():
    """
    Check that a simple test is working.
    """
    assert 2 + 2 == 4, "The simple test failed - oh no!"


def test_pluralize():
    """
    Check plularlise functions imports and works as expected
    """
    assert "boys" == pluralize("boy")
