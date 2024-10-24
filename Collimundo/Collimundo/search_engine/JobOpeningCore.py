
try:
    from .AzureCommunication import AzureCommunication
    from .JobQueryCreator import QueryCreator
    from .OpenAICommunication import OpenAICommunication
except (ModuleNotFoundError, ImportError):
    from AzureCommunication import AzureCommunication
    from JobQueryCreator import QueryCreator
    from OpenAICommunication import OpenAICommunication


class JobOpeningCore:
    """! Class used to guide the whole search process for job openings
    """

    def __init__(self, proxy, debug=False):
        self.debug = debug
        self.proxy = proxy
        self.AzureConnection = AzureCommunication(debug=debug)
        self.OpenAIConnection = OpenAICommunication(debug=debug)
        self.QueryCreator = QueryCreator()
        self.min_result_amount = 5  # amount of results needed for openAI not to be used

    # function used to guide the whole search process
    def search(self, input_string):
        """! Function used to guide the whole search process
        @param input_string: The input string
        """

        query = self.create_query(input_string)
        output, result_amount = self.check_custom_queries(query)
        if result_amount < self.min_result_amount:
            if self.debug:
                print("openAI used, " + str(result_amount) + " results were found without it.")
            try:
                openAI_prompt = self.make_prompt_with_openAI(input_string)
                output["openAI"] = self.filter_duplicates(self.search_with_azure(openAI_prompt))
            except:
                output["openAI"] = None
        else:
            if self.debug:
                print("No openAI used, " + str(result_amount) + " results were found.")
            output["openAI"] = None
        self.submit_result(output)

    # function to create the custom queries without the use of openAI
    def create_query(self, input_string):
        """! Function used to create the custom queries without the use of openAI

        @param input_string: The input string
        """

        return self.QueryCreator.create_query(input_string)

    # function to look up data from the database with a given gremlin query in string format
    def search_with_azure(self, query):
        """! Function used to look up data from the database with a given gremlin query in string format

        @param query: The query

        @return: The results
        """
        return self.AzureConnection.make_request(query, write_prompts=False)

    # function to make a prompt using openAI (only used if the custom prompts did not return enough results)
    def make_prompt_with_openAI(self, input_string):
        """! Function used to make a prompt using openAI (only used if the custom prompts did not return enough results)

        @param input_string: The input string
        
        @return: The prompt
        """
        ans = self.OpenAIConnection.convert("Job openings with respect to the following query: " + input_string, True, 0)
        self.OpenAIConnection.send_shutdown() #because tries = 0, each time the threads will be started again, so this line secures correct thread ending
        return ans

    # function used to submit the results of the search to the proxy as well as set the finished variable to True
    def submit_result(self, result):
        """! Function used to submit the results of the search to the proxy as well as set the finished variable to True

        @param result: The result
        """
        self.proxy.set_result(result)
        self.proxy.set_finished(True)

    # function used to filter duplicates from the results of each category
    def filter_duplicates(self, results):
        """! Function used to filter duplicates from the results of each category

        @param results: The results

        @return: The filtered results
        """
        ids = []
        result = []
        for prompt_result in results:
            for answer in prompt_result:
                if answer['id'] not in ids:
                    ids.append(answer['id'])
                    result.append(answer)
        return result

    # function used to lookup and count all results from the custom queries
    def check_custom_queries(self, custom_queries):
        """! Function used to lookup and count all results from the custom queries

        @param custom_queries: The custom queries

        @return: The results and the amount of results
        """
        results = {}

        # company name
        results["company"] = self.filter_duplicates(self.search_with_azure(custom_queries["company"]))

        # title
        results["title"] = self.filter_duplicates(self.search_with_azure(custom_queries["title"]))

        # place
        results["place"] = self.filter_duplicates(self.search_with_azure(custom_queries["place"]))

        # description
        results["description"] = self.filter_duplicates(self.search_with_azure(custom_queries["description"]))

        result_amount = len(results["company"]) + len(results["title"]) + len(results["place"]) + len(results["description"])

        return results, result_amount
