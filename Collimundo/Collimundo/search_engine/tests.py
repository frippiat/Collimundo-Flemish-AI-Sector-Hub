# external imports
import threading

from numpy import random
import time

# own imports
try:
    from .Proxy import Proxy
except (ModuleNotFoundError, ImportError):
    from Proxy import Proxy


# create the test Proxy in debug mode
test = Proxy(user_id=1, debug=True)


# function to input the test search prompts
def test_function_input():
    """! Function used to test the input of the proxy
    """
    print("start inputting")
    test.search(input_string="TechWolf", final=False)
    for i in range(6):
        test.search("mauhn", final=(i == 5))
        time.sleep(random.uniform(0.1, 0.5))


# function to read the output of the search engine
def test_function_output():
    """! Function used to test the output of the proxy
    """
    print("start checking for output")
    finished = False
    while not finished:
        res = test.get_result()
        if res is not None:
            print(
                "\n...................................\noutput: "
                + str(res)
                + "\n...................................\n"
            )
            test.set_result(None)

        finished = test.is_finished()

    #test the filters
    test.start_applying_filters()
    test.apply_filter_type(["investor", "implementor"])
    test.search_with_filters()
    print(
        "\n...............................................type.......................................................\noutput: "
        + str(test.get_result())
        + "\n..........................................................................................................\n"
    )
    test.apply_filter_socials_present()
    test.search_with_filters()
    print(
        "\n...............................................socials....................................................\noutput: "
        + str(test.get_result())
        + "\n..........................................................................................................\n"
    )
    test.remove_filter()
    test.apply_filter_research_papers_present()
    test.search_with_filters()
    print(
        "\n..............................................research....................................................\noutput: "
        + str(test.get_result())
        + "\n..........................................................................................................\n"
    )
    test.remove_filter()
    test.search_with_filters()
    print(
        "\n..............................................#nofilter...................................................\noutput: "
        + str(test.get_result())
        + "\n..........................................................................................................\n"
    )
    print("\nDONE")


# create and start both test threads
test_thread_output = threading.Thread(target=test_function_output, args=())
test_thread_output.start()
test_thread_input = threading.Thread(target=test_function_input, args=())
test_thread_input.start()

# wait for both threads to finish before ending the main thread.
# Not doing this results in problems when creating other threads and interacting with the database.
test_thread_input.join()
test_thread_output.join()
