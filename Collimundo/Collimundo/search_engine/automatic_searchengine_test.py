import time

from numpy import random

try:
    from .Proxy import Proxy
    from .JobOpeningProxy import JobOpeningProxy
except (ModuleNotFoundError, ImportError):
    from Proxy import Proxy
    from JobOpeningProxy import JobOpeningProxy

"""Here you can write the automatic tests for the search engine.
each function that starts with test_ or ends with _test is going to be ran automatically.
So if you have incomplete tests, watch the name before pushing!"""


def test_companysearchengine():
    """! Test the company search engine.
    """
    return
    TEST_SETTINGS = {
        "intermediate": {
            "max_duration": 5,
            "input": [
                "techwolf",
                "mauhn",
            ],
        },
        "openAI": {
            "max_duration": 20,
            "input": "Everything that has something to do with ai",
        },
    }

    test = Proxy(debug=False)

    # -- Non-OpenAI tests --

    test_settings = TEST_SETTINGS.get("intermediate", {})
    max_duration = test_settings.get("max_duration", 0)

    for input_string in test_settings.get("input", []):
        # time for max duration
        start = time.time()

        print(f"\n> intermediate test: {input_string}")

        # request search
        test.search(input_string=input_string, final=False, chatGPT=False)

        while test.get_result() is None:
            end = time.time()
            if (end - start) > max_duration:
                break
            print(end - start)
            time.sleep(0.5)  # check every half a second

        assert (test.get_result() is not None), f"No result obtained after {max_duration} seconds!!"

        print(f"result: {test.get_result()}")

        # next test
        time.sleep(1)
        test.set_result(None)

    # -- Single OpenAI test --
    test_settings = TEST_SETTINGS.get("openAI", {})
    max_duration = test_settings.get("max_duration", 0)
    input_string = test_settings.get("input", None)
    if input_string is None:
        return

    # time for max duration
    start = time.time()

    print(f"\n> OpenAI test: {input_string}")

    # request search
    test.search(input_string=input_string, final=True, chatGPT=False)

    while test.get_result() is None:
        end = time.time()
        if (end - start) > max_duration:
            break
        time.sleep(random.uniform(0.0, 0.5))  # check every half a second

    assert (
        test.get_result() is not None
    ), f"No result obtained after {max_duration} seconds!!"

    print(f"result: {test.get_result()}")

    # next test
    time.sleep(1)
    test.set_result(None)


def test_jobsearchengine():
    """! Test the job search engine.
    """
    return
    TEST_SETTINGS = {
        "max_duration": 10,
        "input": ["robot engineer", "data scientist"],
    }

    proxy = JobOpeningProxy(debug=False)

    test_settings = TEST_SETTINGS
    max_duration = TEST_SETTINGS.get("max_duration", 0)

    test_input = test_settings.get("input", [])
    for index, input_string in enumerate(test_input):
        # time for max duration
        start = time.time()

        print(f"\n> test: {input_string}")

        # request search
        proxy.search(query=input_string)

        while not proxy.get_finished():
            end = time.time()
            if (end - start) > max_duration:
                break
            time.sleep(0.5)  # check every half a second

        assert (
            proxy.get_result() is not None
        ), f"No result obtained after {max_duration} seconds!!"

        print(f"result: {proxy.get_result()}")

        # next test
        time.sleep(1)
        proxy.set_result(None)
