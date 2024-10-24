# external imports
# import copy
import threading
from pathlib import Path
import os
import time
import json

# own imports
try:
    from .AzureCommunication import AzureCommunication
    from .CustomGremlinQueries import CustomGremlinQueries
    from .OpenAICommunication import OpenAICommunication
    from .QuerySyntaxChecker import QuerySyntaxChecker
    from .Exceptions import CouldNotRetrieveResult, NoValidOpenAIResult
    from .embedding import Ranker
except (ModuleNotFoundError, ImportError):
    from AzureCommunication import AzureCommunication
    from CustomGremlinQueries import CustomGremlinQueries
    from OpenAICommunication import OpenAICommunication
    from QuerySyntaxChecker import QuerySyntaxChecker
    from Exceptions import CouldNotRetrieveResult, NoValidOpenAIResult
    from embedding import Ranker


# Core class. Can be used through the proxy. The core takes care of the communication
# between the proxy, the openAI connection and the database connection.
class Core:
    """! Class used to guide the whole search process for companies
    """
    def __init__(self, proxy, user_id, debug):
        self.__input = AtomicVariable()
        self.result = {"chatGPT": None, "custom": None}
        self.__check_thread = threading.Thread(
            target=self.check_queue, name="core_checking_thread", args=()
        )
        self.__check_thread.start()
        self.proxy = proxy
        self.azure_connection = AzureCommunication(user_id, debug)
        self.OpenAI_connection = OpenAICommunication(debug)
        self.ranker = Ranker(self.azure_connection, debug)
        self.syntaxChecker = QuerySyntaxChecker(debug)
        self.customQueries = CustomGremlinQueries(self.azure_connection, self.ranker, debug)
        self.user_id = user_id
        self.debug = debug
        self.finished = False

        location = Path(__file__).resolve().parent
        self.log_file = os.path.join(location, "data/search_log.txt")

    # Function that runs in a separate thread and checks the queue for new inputs from the core.
    # When new inputs are found this function makes calls to all needed components
    # to answer the search prompt.
    # When a new input is discovered in the middle of this proces,
    # the proces is stopped and restarted for the new input.
    def check_queue(self):
        """! Function that runs in a separate thread and checks the queue for new inputs from the core.
        When new inputs are found this function makes calls to all needed components to answer the search prompt.
        When a new input is discovered in the middle of this proces, the proces is stopped and restarted for the new input.
        """
        final = False
        tries = 0
        max_tries = 2
        while not final:
            if self.__input.get_value() is not None:

                # wipe the previous search history
                self.wipe_search_history()

                input_string, final, chatGPT, filters = self.__input.get_and_clear()

                self.log_info(f"{self.user_id} - User input - " + str(input_string))

                if self.debug:
                    print("Core found input as " + str(input_string))

                # custom result
                self.result[
                    "custom"
                ] = self.customQueries.extract_companies_and_connected(input_string.lower(), filters)

                if len(self.result["custom"]["base_companies"]) == 0:
                    self.result["custom"] = None

                # GPT result
                if self.result["custom"] is None and chatGPT:  # if query was NOT just a name -> use GPT

                    try:
                        gpt_result = self.get_gpt_result(input_string, final, tries, filters)
                        self.log_info(f"{self.user_id} - GPT result - " + str(gpt_result))
                    except Exception as e:
                        self.log_info(f"{self.user_id} - Error - " + str(e))
                        gpt_result = "d"

                    if self.__input.get_value() is None and gpt_result is not None:
                        res = []

                        # get the results from the database
                        for res_ in self.get_azure_result(gpt_result):
                            res.extend(res_)

                        # rank the results
                        ranked_res = self.ranker.rank_on_query(res, input_string)

                        # set and log the final result
                        self.result["chatGPT"] = ranked_res
                        self.log_info(f"{self.user_id} - Final result - " + str(self.result["chatGPT"])[:200] + "...")
                        
                        if final:
                            tries += 1

                    # If open AI services are unavailable
                    else:
                        self.result["chatGPT"] = []
                        if self.debug:
                            print("Discarded old input: " + str(input_string))

                    # done?
                    if (
                        "Something went wrong" in self.result["chatGPT"]
                        and final
                        and tries < max_tries
                    ):
                        # self.__input.set_if_none(input_string, copy.deepcopy(final))
                        # final = False
                        # print("retry request")
                        self.proxy.set_result({"chatGPT": None, "custom": None})
                    else:
                        if len(self.result["chatGPT"]) == 0:
                            self.result["chatGPT"] = None
                        self.proxy.set_result(self.result)
                else:
                    self.log_info(f"{self.user_id} - Used custom search - found {self.result['custom']['base_companies'][0]}")
                    self.proxy.set_result(self.result)

        if self.debug:
            print("Stopped checking queue\n")
        self.finished = True
        self.OpenAI_connection.send_shutdown()

    # function used by the core to add a new input value to the queue
    def set_input(self, input_string: str, final, chatGPT, filters=[]):
        """! Function used by the core to add a new input value to the queue

        @param input_string: The input string
        @param final: The final variable
        @param chatGPT: The chatGPT variable
        @param filters: The filters
        """
        self.__input.set(input_string, final, chatGPT, filters)

    # function to get the result from the core
    def get_result(self):
        """! Function to get the result from the core

        @return: The result
        """
        return self.result

    # function to make a call to the openAI connection to convert an input string to a gremlin prompt
    def get_gpt_result(self, input_string, final, tries, filters = None):
        """! Function to make a call to the openAI connection to convert an input string to a gremlin prompt

        @param input_string: The input string
        @param final: The final variable
        @param tries: The tries variable
        @param filters: The filters
        
        @return: The gremlin prompt
        """
        try:
            return self.OpenAI_connection.convert(input_string, final, tries, filters)
        except NoValidOpenAIResult:
            return None

    # function to make a call to the database connection to submit a prompt and return the results from the database
    def get_azure_result(self, prompt, write_prompts = True):
        """! Function to make a call to the database connection to submit a prompt and return the results from the database

        @param prompt: The prompt
        @param write_prompts: The write_prompts variable

        @return: The results from the database
        """

        prompt = self.syntaxChecker.check(prompt)
        self.log_info(f"{self.user_id} - Syntax checked - " + str(prompt))
        try:
            return self.azure_connection.make_request(prompt, write_prompts)
        except CouldNotRetrieveResult:
            return [[] for i in range(len(prompt))]

    # log to file
    def log_info(self, info):
        """! Function to log information to a file

        @param info: The information to log
        """
        current_time = time.localtime()
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S", current_time)
        with open(self.log_file, "a") as log_file:
            log_file.write(timestamp + " : " + info + "\n")

    def wipe_search_history(self):
        """! Function to wipe the search history of the user
        """
        directory = "search_history_per_user"
        file_name = "search_history_user_" + str(self.user_id) + ".txt"
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print("Previous search history deleted successfully.")
        else:
            print("Previous search history does not exist.")


# AtomicVariable is used for the __input variable in the core. This value can be changed
# by a number of different threads, so it should be made atomic.
class AtomicVariable:
    """! Class used to make a variable atomic
    """
    def __init__(self, initial_value=None, final=False, chatGPT=False, filters=[]):
        self._value = initial_value
        self.final = final
        self.chatGPT = chatGPT
        self.filters = filters
        self._lock = threading.Lock()

    # function to get the value of the atomic variable and set the variable to None
    def get_and_clear(self):
        """! Function to get the value of the atomic variable and set the variable to None

        @return: The value, final, chatGPT and filters
        """
        with self._lock:
            value = self._value
            final = self.final
            chatGPT = self.chatGPT
            filters = self.filters
            self._value = None
            self.final = False
            self.chatGPT = False
            self.filters = []
            return (value, final, chatGPT, filters)

    # function to set the atomic variable
    def set(self, value, final, chatGPT, filters=[]):
        """! Function to set the atomic variable

        @param value: The value
        @param final: The final variable
        @param chatGPT: The chatGPT variable
        @param filters: The filters
        """
        with self._lock:
            self._value = value
            self.final = final
            self.chatGPT = chatGPT
            self.filters = filters

    # function to get the value of the atomic variable
    def get_value(self):
        """! Function to get the value of the atomic variable

        @return: The value
        """
        return self._value

    # function to set the variable only if the value is none
    def set_if_none(self, value, final, chatGPT, filters=[]):
        """! Function to set the variable only if the value is none

        @param value: The value
        @param final: The final variable
        @param chatGPT: The chatGPT variable
        @param filters: The filters
        """
        with self._lock:
            if self._value is None:
                self._value = value
                self.final = final
                self.chatGPT = chatGPT
                self.filters = filters
                return True
            else:
                return False
