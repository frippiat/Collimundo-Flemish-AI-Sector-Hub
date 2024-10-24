# own imports
from pathlib import Path
import os
import time
import json

try:
    from .main import Core
except (ModuleNotFoundError, ImportError):
    from main import Core


# Proxy to be used by general application when interacting with the search engine
class Proxy:
    """! Class used to guide the whole search process for job openings. This is a proxy class for the Core class.
    """
    def __init__(self, user_id=1, debug=False):
        self.core = Core(self, user_id, debug)
        self.user_id = user_id
        self.debug = debug
        self.result = None
        self.filtered_result_ready = True
        self.filter_prompts = []
        location = Path(__file__).resolve().parent
        self.search_history_file = os.path.join(
            location,
            f"search_history_per_user/search_history_user_{user_id}.txt"
        )

    # function used to give a search prompt to the search engine
    # the value of final_value should be True when the user is finished writing their prompt.
    # While the prompt is being written, intermediate results can be generated when setting final_value to False.
    def search(self, input_string, final=False, chatGPT=True, filters=[]):
        """! Function used to give a search prompt to the search engine

        @param input_string: The search query
        @param final: Whether the search query is final
        @param chatGPT: Whether the search query is a chatGPT query
        @param filters: The filters to apply
        """
        self.clear_history()
        self.save_query_to_history(input_string)
        if self.debug:
            print("Searching for " + input_string + "; final: " + str(final))
        self.core.set_input(input_string, final, chatGPT, filters)

    # function used to give a filter the previous search result
    def filter(self, filters):
        """! Function used to give a filter the previous search result

        @param filters: The filters to apply
        """

        self.start_applying_filters()
        if self.filter_prompts: # if there is a history
            if self.filter_prompts[0][0] == "C":
                function_name, function_param = self.filter_prompts[0][4:].split(" - ")
                function_param = json.loads(function_param)
                self.search_custom_query(function_name, function_param, filters)
            else:
                self.apply_filter_type(filters)  # TODO: for now only filter on actor type
                self.search_with_applied_filters()
        else:
            self.result = {"chatGPT": None, "custom": None}
            self.filtered_result_ready = True

    # function used by the core to set the result in the proxy
    def set_result(self, result):
        """! Function used by the core to set the result in the proxy

        @param result: The result
        """
        # print(result)
        self.result = result
        return

    # function used by the general application to get the result out of the proxy
    def get_result(self, wait=False):
        """! Function used by the general application to get the result out of the proxy

        @param wait: Whether to wait for the result
        @return: The result
        """
        if wait:
            while self.result is None:
                time.sleep(0.1)
        return self.result

    # function used by the general application to get the result out of the proxy
    def get_filtered_result(self, wait=False):
        """! Function used by the general application to get the result out of the proxy

        @param wait: Whether to wait for the result
        @return: The result
        """
        if wait:
            while not self.filter_is_finished():
                time.sleep(0.1)
        return self.result

    # function that can be used by the general application to see whether the result saved in
    # the proxy is the final result.
    def is_finished(self):
        """! Function that can be used by the general application to see whether the result saved in the proxy is the final result.

        @return: Whether the result is final
        """
        return self.core.finished
        

    def filter_is_finished(self):
        """! Function that can be used by the general application to see whether the result saved in the proxy is the final result. For filter operations.

        @return: Whether the result is final
        """
        return self.filtered_result_ready

    def clear_history(self):
        """! Function used to clear the search history
        """
        with open(self.search_history_file, 'w') as file:
            file.write("")

    def save_query_to_history(self, query):
        """! Function used to save a query to the search history

        @param query: The query to save
        """
        with open(self.search_history_file, 'a') as file:
            file.write(query + "\n")

    def read_unfiltered_prompts(self):
        """! Function used to read the unfiltered prompts from the search history
        """
        self.filter_prompts = []
        self.filter_query = ""
        first = True
        try:
            with open(self.search_history_file, 'r') as file:
                for line in file:
                    if first:
                        self.filter_query = line.strip()
                        first = False
                    else:
                        self.filter_prompts.append(line.strip())
        except FileNotFoundError:
            pass

    def add_to_unfiltered_prompts(self, input_string):
        """! Function used to add a filter to the unfiltered prompts

        @param input_string: The filter to add
        """
        prompts = []

        for prompt in self.filter_prompts:

            parts = prompt.split(".")
            # last part is always .dedup()
            # check if before last part is .limit()
            # if so place it before .limit() that else before .dedup()
            fill_index = -2 if parts[-2].startswith("limit(") else -1
            prefix = ".".join(parts[:fill_index])
            suffix = "." + ".".join(parts[fill_index:])

            # if '.in(' in prompt:
            #     last_index = prompt.rfind(".in(")
            #     prefix = prompt[:last_index]
            #     suffix = prompt[last_index:]
            #     last_index = suffix.find(")")
            #     prefix = prefix + suffix[:last_index + 1]
            #     suffix = suffix[last_index + 1:]
            # else:
            #     prefix = "g.V()"
            #     suffix = prompt[5:]

            prompt = prefix + input_string + suffix

            prompts.append(prompt)

        print(prompts)
        self.filter_prompts = prompts

    def start_applying_filters(self):
        """! Function used to start applying filters
        """
        self.read_unfiltered_prompts()

    def apply_filter_type(self, type_list):
        """! Function used to apply a type filter

        @param type_list: The types to filter on
        """
        type_str = ""
        for type in type_list:
            type_str += "'" + type + "',"
        type_str = type_str[:-1]
        self.add_to_unfiltered_prompts(".has('actor', within(" + type_str + "))")

    def apply_filter_research_papers_present(self):
        """! Function used to apply a filter for research papers being present
        """
        self.add_to_unfiltered_prompts(".has('papers')")

    def apply_filter_socials_present(self):
        """! Function used to apply a filter for socials being present
        """
        self.add_to_unfiltered_prompts(".or(has('linkedin'),has('twitter'),has('facebook'),has('instagram'))")

    def remove_filter(self):
        """! Function used to remove a filter
        """
        if self.debug:
            print("Removing filters")
        self.read_unfiltered_prompts()

    def search_with_applied_filters(self):
        """! Function used to search with the applied filters
        """
        self.filtered_result_ready = False
        res = []
        for res_ in self.core.get_azure_result(self.filter_prompts, False):
            res.extend(res_)
        # rank the results
        ranked_res = self.core.ranker.rank_on_query(res, self.filter_query)
        self.result = {"chatGPT": ranked_res, "custom": None}
        self.filtered_result_ready = True

    def search_custom_query(self, function_name, function_input, filters):
        """! Function used to search with a custom query

        @param function_name: The name of the custom query
        @param function_input: The input for the custom query
        @param filters: The filters to apply
        """
        self.filtered_result_ready = False
        self.result = {"chatGPT": None, "custom": self.core.customQueries.execute_filtered_function(function_name, function_input, filters)}
        self.filtered_result_ready = True
