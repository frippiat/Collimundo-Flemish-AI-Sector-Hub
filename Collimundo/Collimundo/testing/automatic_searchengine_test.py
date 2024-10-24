import threading
import time

from numpy import random
from pathlib import Path
try:
    from Collimundo.search_engine.Proxy import Proxy
    from Collimundo.search_engine.JobOpeningProxy import JobOpeningProxy
except (ModuleNotFoundError, ImportError):
    from Proxy import Proxy
    from JobOpeningProxy import JobOpeningProxy

"""Here you can write the automatic tests for the search engine.
each function that starts with test_ or ends with _test is going to be ran automatically.
So if you have incomplete tests, watch the name before pushing!"""


def test_searchengine():
    TEST_SETTINGS = {
        "intermediate": {
            "max_duration": 5,
            "input": [
                "collimundotest",
                "universitytest",
            ],
        },
        "openAI": {
            "max_duration": 10,
            "input": "All alumni companies from universitytest",
        },
    }

    """up till now: just testing availability"""
    test = Proxy(debug=True)

    # -- Non-OpenAI tests --

    test_settings = TEST_SETTINGS.get("intermediate", {})
    max_duration = test_settings.get("max_duration", 0)

    for input_string in test_settings.get("input", []):
        # time for max duration
        start = time.time()

        print(f"\n> intermediate test: {input_string}")

        # request search
        test.search(input_string=input_string, final=False)

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
    test.search(input_string=input_string, final=True)

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


def job_se(test_proxy, query):
    test_proxy.search(query=query)

    start = time.time()
    diff = 0
    while diff < 10:  # job search engine should also work in 10 seconds max
        finished = test_proxy.get_finished()
        if finished:
            result = test_proxy.get_result()
            test_proxy.set_finished(False)
            break
        diff = time.time() - start
    assert diff < 10, "job searches take to long!!"
    assert result != None, "available vacancy was not found!"



def test_job_search_engine():
    # Determine the script directory
    script_dir = Path(__file__).resolve().parent

    # Path to the unique_id.txt file
    unique_id_file = script_dir / 'unique_id.txt'

    # Ensure the file exists before trying to read it
    assert unique_id_file.exists(), "no unique id file to delete the subsystem!"

    # Get unique id from the file
    with unique_id_file.open('r') as f:
        unique_test_id = f.read().strip()

    test_proxy = JobOpeningProxy()

    #test with multithreading
    thread1 = threading.Thread(target=job_se, args=(test_proxy, f"CollimundoTest_{unique_test_id}"))
    thread2 = threading.Thread(target=job_se, args=(test_proxy, f"Test Manager"))
    thread1.start()
    thread2.start()
    thread2.join()
    thread1.join()
