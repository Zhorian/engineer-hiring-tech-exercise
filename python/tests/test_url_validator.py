from src.url_validator import validate_url

def test_validate_url_valid():
    assert validate_url("http://example.com") == True
    assert validate_url("https://www.google.com") == True

def test_validate_url_invalid():
    assert validate_url("invalid-url") == False
    assert validate_url("") == False
    assert validate_url("ftp://example.com") == True  # ftp has scheme and netloc