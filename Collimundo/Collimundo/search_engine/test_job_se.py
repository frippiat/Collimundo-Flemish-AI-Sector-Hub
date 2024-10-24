# external imports
import threading
import time

from numpy import random

from JobOpeningProxy import JobOpeningProxy

test_proxy = JobOpeningProxy()

def test_input():
    """! Function used to test the input of the proxy
    """
    print("start inputting")
    test_proxy.search(query="Mauhn")
    for i in range(6):
        test_proxy.search(query=f"Robotics Engineer")
        time.sleep(random.uniform(0.1, 0.5))


def test_output():
    """! 
    Function used to test the output of the proxy
    """
    print("start looking for output")
    while True:
        finished = test_proxy.get_finished()
        if finished:
            result = test_proxy.get_result()
            print(f"Found output {result}")
        test_proxy.set_finished(False)

# create and start both test threads
test_thread_output = threading.Thread(target=test_input, args=())
test_thread_output.start()
test_thread_input = threading.Thread(target=test_output, args=())
test_thread_input.start()

# wait for both threads to finish before ending the main thread.
# Not doing this results in problems when creating other threads and interacting with the database.
test_thread_input.join()
test_thread_output.join()