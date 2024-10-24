# external imports
from pathlib import Path
import os
import copy
import threading
import time
from queue import Queue
from openai import OpenAI, RateLimitError, NotFoundError
from numpy import random
import json


try:
    from Modifiability.keystructure import keymaster
except (ModuleNotFoundError, ImportError):
    from Collimundo.Modifiability.keystructure import keymaster


try:
    from .Exceptions import NoValidOpenAIResult
    from .OpenAIFilterModifier import OpenAIFilterModifier
except (ModuleNotFoundError, ImportError):
    from Exceptions import NoValidOpenAIResult
    from OpenAIFilterModifier import OpenAIFilterModifier


# Class used to send the right search prompts to the openAI request dispatcher
# and generate a simple gremlin prompt for the others.
class OpenAICommunication:
    """! Class used to communicate with openAI
    Class used to send the right search prompts to the openAI request dispatcher and generate a simple gremlin prompt for the others.
    """
    def __init__(self, debug):
        self.RequestDispatcher = OpenAIRequestDispatcher()
        self.response_ready = False
        self.response = None
        self.response_finished_lock = threading.Lock()
        self.debug = debug
        self.OpenAIFilterModifier = OpenAIFilterModifier()

    # function used by the core to convert a search prompt into a gremlin prompt.
    # If final is True, openAI will be used to generate the gremlin prompt,
    # otherwise simple gremlin prompts will be generated for each word in the search prompt
    def convert(self, input_string, final, tries, filter = None):
        """! Function used to convert a search prompt into a gremlin prompt.
        If final is True, openAI will be used to generate the gremlin prompt, otherwise simple gremlin prompts will be generated for each word in the search prompt

        @param input_string: The input string
        @param final: Whether it is the final request
        @param tries: The amount of tries
        @param filter: The filter

        @return: The gremlin prompt
        """

#         # don't use openAI when it is not the final request
#         if not final:  # TEMP
#             # for now return "No" when it is not the final request in order to avoid problems with database lookup
#             self.response = ["No"]
#             # implement efficient search for company name (fuzzysearch)
#             self.response = input_string.split(" ")
#             blacklist = [
#                 "the",
#                 "of",
#                 "in",
#                 "a",
#                 "an",
#                 "and",
#                 "or",
#                 "is",
#                 "are",
#                 "it",
#                 "its",
#                 "to",
#                 "for",
#                 "with",
#                 "on",
#                 "by",
#                 "at",
#                 "as",
#                 "be",
#                 "from",
#                 "that",
#                 "this",
#                 "which",
#                 "when",
#                 "where",
#                 "who",
#                 "how",
#                 "why",
#                 "it's",
#                 "i",
#             ]
#             self.response = [
#                 f"g.V().has('name_lower', '{name}').as('source')\
# .both().hasLabel('domain').as('domain')\
# .both().not(where(eq('source'))).as('linked_id')\
# .select('source', 'domain', 'linked_id')\
# .by(values('id'))\
# .by(values('name'))\
# .by(values('id'))\
# .dedup()"
#                 for name in self.response
#                 if name.lower() not in blacklist and len(name) >= 3
#             ]  # vb ML6

#             return self.response

        if tries == 0:
            self.RequestDispatcher.start_thread()

        # Send a completion call to generate an answer
        self.RequestDispatcher.enqueue(input_string, self)

        # busy waiting
        finished = False
        while not finished:
            with (self.response_finished_lock):
                finished = self.response_ready
            time.sleep(0.010)

        with (self.response_finished_lock):
            self.response_ready = False

        response = self.response
        if isinstance(response[0], NoValidOpenAIResult):
            raise response[0]
        else:
            if filter:
                response = self.OpenAIFilterModifier.add_type_filter(response, filter)
            return response

    # function used to set the response withing the OpenAICommunication class and signal that the response is ready
    def set_response(self, response):
        """! Function used to set the response withing the OpenAICommunication class and signal that the response is ready

        @param response: The response
        """
        self.response = response
        with (self.response_finished_lock):
            self.response_ready = True

    # function used by the core to stop the thread in the openAIRequestDispatcher
    def send_shutdown(self):
        """! Function used to stop the thread in the openAIRequestDispatcher
        """
        self.RequestDispatcher.stop_thread()


# Singleton class to guarantee that there is only one OpenAIRequestDispatcher in the system
class Singleton:
    """! Singleton class to guarantee that there is only one OpenAIRequestDispatcher in the system
    """
    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


# retry decorator to make the requests to openAI with exponential backoff if the rate limit is exceeded
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    errors: tuple = (RateLimitError,),
):
    """! Retry a function with exponential backoff

    @param func: The function
    @param initial_delay: The initial delay
    @param exponential_base: The exponential base
    @param jitter: The jitter
    @param max_retries: The maximum amount of retries
    @param errors: The errors

    @return: The wrapper
    """

    def wrapper(*args, **kwargs):
        # Initialize variables
        num_retries = 0
        delay = initial_delay

        # Loop until a successful response or max_retries is hit or an exception is raised
        while True:
            try:
                # print("trying", num_retries, "times")
                return func(*args, **kwargs)

            # Retry on specified errors
            except errors:
                # Increment retries
                num_retries += 1

                # print("failed", num_retries, "times")

                # Check if max retries has been reached
                if num_retries > max_retries:
                    raise Exception(
                        f"Maximum number of retries ({max_retries}) exceeded."
                    )

                # Increment the delay
                delay *= exponential_base * (1 + jitter * random.random())

                # Sleep for the delay
                time.sleep(delay * 0.01)

            # Raise exceptions for any errors not specified
            except Exception as e:
                raise e

    return wrapper


# Class used to dispatch requests to openAI
class OpenAIRequestDispatcher(Singleton):
    def __init__(self):
        self.requests = Queue()
        self._lock = threading.Lock()
        self.request_sending_thread = threading.Thread(
            target=self.send_requests, name="request_sending_thread", args=()
        )
        self.thread_running = 0
        self.thread_running_lock = threading.Lock()
        self.start_stop = threading.Lock()
        self.finished = [False]
        self.keymaster = keymaster()
        self.client = OpenAI(
            api_key=self.keymaster.openaikey
        )
        self.deployment_name = self.keymaster.search_model
        # self.request_sending_thread.start()

    # function used by the OpenAICommunication class to add a request to the dispatch queue
    def enqueue(self, request, requester):
        with (self._lock):
            # print("submitted request")
            self.requests.put((request, requester))

    # function that runs in a separate thread and dispatches requests to openAI
    def send_requests(self):
        with self.thread_running_lock:
            thread_running = self.thread_running
            if self.thread_running == 0:
                print(thread_running)
        while thread_running != 0:
            if not self.requests.empty():
                # print("received request")
                next_request = self.requests.get()
                print("Requesting GPT query")

                # Get GPT prompt
                GPT_prompt = "Something went wrong"
                location = Path(__file__).resolve().parent
                # get sys message + trainingsdata out of file -> just copy paste list of message attribute out of the playground and paste it in this file
                with open(os.path.join(location, 'data/trainings_data_GPT4.txt'), 'r') as file:
                    content = file.read()
                messages = json.loads(content)
                messages.append({"role": "user", "content": str(next_request[0])})
                response = self.completions_with_backoff(
                    model=self.deployment_name,
                    messages=messages,
                    temperature=1,
                    max_tokens=256,
                    top_p=0.3,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                print("Received result GPT result")

                if not isinstance(response, NoValidOpenAIResult):
                    response = response.choices[0].message.content
                next_request[1].set_response([response])
                # else:
                    # next_request[1].set_response([response])

            with self.thread_running_lock:
                thread_running = self.thread_running
        print("openAI Request Dispatcher Stopped")

    # function to start the dispatcher thread
    def start_thread(self):
        self.start_stop.acquire()
        self.thread_running_lock.acquire()
        self.thread_running += 1 # an extra process uses the thread to gain search results
        thread_running = copy.deepcopy(self.thread_running)
        self.thread_running_lock.release()
        if thread_running == 1:
            self.request_sending_thread.start()
        self.start_stop.release()

    # function to stop the dispatcher thread
    def stop_thread(self):
        self.start_stop.acquire()
        self.thread_running_lock.acquire()
        self.thread_running -= 1
        thread_running = copy.deepcopy(self.thread_running)
        self.thread_running_lock.release()

        if thread_running == 0: #if this was the last process using the thread -> stop it (its function will stop when self.running = 0
            self.request_sending_thread.join() #wait till thread fully finished
        self.start_stop.release()

    # function to send requests to openAI with exponential backoff in case the rate limit is exceeded
    @retry_with_exponential_backoff
    def completions_with_backoff(self, **kwargs):
        try:
            return self.client.chat.completions.create(**kwargs)
        except NotFoundError as e:
            return NoValidOpenAIResult(f"OpenAI exception: {e.body}")
        except Exception as e:
            return NoValidOpenAIResult(f"OpenAI exception: {e.__class__}")
