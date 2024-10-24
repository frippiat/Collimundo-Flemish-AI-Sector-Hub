from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse
from django.test.testcases import DatabaseOperationForbidden
from django.core.exceptions import ImproperlyConfigured

class UrlsAvailabilityTest(SimpleTestCase):
    def test_urls(self):
        for app in settings.TEST_APPS:
            exec(
                f"""
from {app}.urls import urlpatterns
print("\\n-- {app.capitalize()} --")
for url_pattern in urlpatterns:
    self.check_url_availability(url_pattern)
            """
            )

    def check_url_availability(self, url_pattern):
        if "<" in url_pattern.pattern._route:
            return

        url_name = getattr(url_pattern, "name", None)
        code = 200
        args = ""

        # check for special urls
        if url_name in settings.SPECIAL_LINKS:
            # leave out urls
            if settings.SPECIAL_LINKS[url_name] is None:
                return
            # special return code and args
            code = settings.SPECIAL_LINKS[url_name].get("code", code)
            args = settings.SPECIAL_LINKS[url_name].get("args", args)

        # get url path
        url_path = reverse(url_name) if url_name else url_pattern.pattern._route

        # add query args
        url_path += args

        try:
            response = self.client.get(url_path)
        except DatabaseOperationForbidden:
            print(f"SKIPPED (Forbidden to access database in test, resulted in skip) - '{url_path}'")
            return
        except ImproperlyConfigured:
            print(f"SKIPPED (Improperly configured database settings, resulted in skip) - '{url_path}'")
            return
        
        self.assertEqual(
            response.status_code,
            code,
            f"UNAVAILABLE (expected {code} got {response.status_code}) - '{url_path}'",
        )
        print(f"AVAILABLE ({code}) - '{url_path}'")
