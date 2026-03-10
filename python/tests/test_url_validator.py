from src.url_validator import validate_url, is_crawlable

class TestClass:
    def test_validate_url_valid(self):
        assert validate_url("http://example.com")
        assert validate_url("http://eXample.com")
        assert validate_url("https://www.google.com")

    def test_validate_url_invalid(self):
        assert not validate_url("invalid-url")
        assert not validate_url("")
        assert not validate_url("ftp://example.com") # ftp has scheme and netloc
        assert not validate_url("www.example.com") 

    def test_url_not_in_root_path(self):
        root_path = "www.example.com"
        disallowed_paths = []

        assert not is_crawlable("https://www.facebook.com", root_path, disallowed_paths)
        assert not is_crawlable("https://www.example.co.uk", root_path, disallowed_paths)

    def test_url_in_root_path(self):
        root_path = "www.example.com"
        disallowed_paths = []

        assert is_crawlable("www.example.com", root_path, disallowed_paths)
        assert is_crawlable("https://www.example.com", root_path, disallowed_paths)
        assert is_crawlable("http://www.example.com", root_path, disallowed_paths)

    def test_url_in_disallowed_paths(self):
        root_path = "www.example.com"
        disallowed_paths = [f"{root_path}/admin/"]

        assert not is_crawlable("www.example.com/admin/", root_path, disallowed_paths)
        assert not is_crawlable("www.example.com/admin", root_path, disallowed_paths)
        assert not is_crawlable("www.example.com/ADMIN", root_path, disallowed_paths)
        assert not is_crawlable("www.example.com/Admin", root_path, disallowed_paths)
        assert not is_crawlable("www.example.com/aDmin", root_path, disallowed_paths)
        assert not is_crawlable("www.example.com/admin.html", root_path, disallowed_paths)


    def test_url_not_in_disallowed_paths(self):
        root_path = "www.example.com"
        disallowed_paths = [f"{root_path}/admin/"]

        assert is_crawlable("www.example.com/administration/", root_path, disallowed_paths)
        assert is_crawlable("www.example.com/super-fun-content", root_path, disallowed_paths)
        assert is_crawlable("www.example.com/super-fun-content.html", root_path, disallowed_paths)
        assert is_crawlable("www.example.com/super-fun-content.html?abc=123", root_path, disallowed_paths)

    def test_url_is_not_path_to_page(self):
        root_path = "www.example.com"
        disallowed_paths = [f"{root_path}/admin/"]

        assert not is_crawlable("https://www.example.com/file.pdf?download=true", root_path, disallowed_paths)
        assert not is_crawlable("https://www.example.com/file.txt", root_path, disallowed_paths)

    def test_url_zego_scooter(self):
        root_path = "www.zego.com"
        disallowed_paths = [
            'http://www.zego.com/admin/','https://www.zego.com/admin/', 'http://www.zego.com/login', 'https://www.zego.com/login', 'http://www.zego.com/signup',
            'https://www.zego.com/signup', 'http://www.zego.com/bypass-onboarding-verify-email', 'https://www.zego.com/bypass-onboarding-verify-email', 'http://www.zego.com/email-verification-confirmation',
            'https://www.zego.com/email-verification-confirmation', 'http://www.zego.com/password-reset', 'https://www.zego.com/password-reset', 'http://www.zego.com/verify-email', 'https://www.zego.com/verify-email',
            'http://www.zego.com/onboarding/', 'https://www.zego.com/onboarding/', 'http://www.zego.com/purchase/', 'https://www.zego.com/purchase/'
        ]

        assert is_crawlable("http://zego.com/scooter/", root_path, disallowed_paths)