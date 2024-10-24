# external imports
import threading

# own imports
try:
    from .Proxy import Proxy
except (ModuleNotFoundError, ImportError):
    from Proxy import Proxy

# create test Proxy
test = Proxy(debug=True)


# function to input test data
def test_function_input():
    """! Function used to test the input of the proxy (with entring of search queries)
    """
    print("start inputting - enter 'stop' to stop")
    inp = input("> ")
    while inp != "stop":
        test.search(inp, final=False)
        inp = input("> ")
    inp = input("final = true > ")
    test.search(inp, final=True)


# function to read the output from the search engine
def test_function_output():
    """! Function used to test the output of the proxy
    """
    print("start checking for output")
    finished = False
    while not finished:
        res = test.get_result(wait=True)
        if res is not None:
            print(
                "\n...................................\noutput: "
                + str(res)
                + "\n...................................\n"
            )
            test.set_result(None)
            finished = test.is_finished()
    print("\nDONE")


# create and start both testing threads
test_thread_output = threading.Thread(target=test_function_output, args=())
test_thread_output.start()
test_thread_input = threading.Thread(target=test_function_input, args=())
test_thread_input.start()


# wait for both threads to finish before ending the main thread.
# Not doing this results in problems when creating other threads and interacting with the database.
test_thread_input.join()
test_thread_output.join()
