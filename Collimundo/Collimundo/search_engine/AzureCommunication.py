# from azure.core.exceptions import AzureError #unused
# from azure.cosmos import CosmosClient  # , PartitionKey #unused
# from azure.identity import DefaultAzureCredential
# import sys
from pathlib import Path
import os

# external imports
# try:
#     import asyncio
# except Exception:
#     pass

try:
    from .GremlinGraphManager import GremlinGraphManager
    from .Exceptions import NoConnectionToDatabase, InvalidGremlinSyntax, CouldNotRetrieveResult
except (ModuleNotFoundError, ImportError):
    from GremlinGraphManager import GremlinGraphManager
    from Exceptions import NoConnectionToDatabase, InvalidGremlinSyntax, CouldNotRetrieveResult

# import time # unused

# from numpy import random # unused

# from cosmos import execute_query
# from gremlin_python.driver import client, serializer

# Singleton class used to make sure there is only one AzureCommunicationClient
class Singleton:
    """! Singleton class used to make sure there is only one AzureCommunicationClient
    """
    def __new__(cls, *args, **kw):
        if not hasattr(cls, "_instance"):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


# Class used to keep the GremlinGraphManager
class AzureCommunicationClient(Singleton):
    """! Class used to keep the GremlinGraphManager
    """
    def __init__(self):
        self.GremlinGraphManager = GremlinGraphManager()


# Class used by the core to communicate with the database.
class AzureCommunication:
    """! Class used by the core to communicate with the database.
    """

    def __init__(self, user_id=1, debug=False):
        """! Constructor
        @param user_id: The user id (used to store the search history per user)
        @param debug: Debug mode (default: False)
        """

        self.client = AzureCommunicationClient()
        self.user_id = user_id
        self.debug = debug
        location = Path(__file__).resolve().parent
        self.search_history_file = os.path.join(
            location,
            f"search_history_per_user/search_history_user_{user_id}.txt"
        )

    # function used to write prompts to the search history
    def write_to_search_history(self, list_of_prompts):
        """! Function used to write prompts to the search history

        @param list_of_prompts: List of prompts
        """

        with open(self.search_history_file, 'a') as file:
            for prompt in list_of_prompts:
                file.write(prompt + '\n')

    # function used by the core to write a custom text to the search history
    def save_custom_query_exec(self, function_name, query):
        """! Function used by the core to write a custom text to the search history

        @param function_name: The function name
        @param query: The query
        """

        prompt = f"C - {function_name} - {query}"
        self.write_to_search_history([prompt])

    # function used by the core to make a database request
    def make_request(self, input_string, write_prompts = False):
        """! Function used by the core to make a database request

        @param input_string: The input string
        @param write_prompts: Write prompts to the search history (default: False)
        """

        response = []

        # write prompts to the search history (to be able to apply filters later)
        if write_prompts:
            self.write_to_search_history(input_string)

        # get results from the database
        for prompt in input_string:
            if self.debug:
                print("prompt: " + prompt)
            if prompt == "No":
                response += ["Something went wrong"]
            else:
                try:
                    response += self.client.GremlinGraphManager.submit_query(
                        query=prompt,
                        read_only=True #important! no write access
                    )
                except NoConnectionToDatabase:
                    raise CouldNotRetrieveResult("Could not connect to database")
                except InvalidGremlinSyntax:
                    raise CouldNotRetrieveResult("Gremlin query had invalid syntax")
                except Exception as e:
                    raise CouldNotRetrieveResult(f"Received exception: {e.__class__}")

        return response

    # function used by the core to get the result from the database
    def get_company_info(self, company_id):
        """! Function used by the core to get the result from the database

        @param company_id: The company id
        """

        query = f"g.V().has('id', '{company_id}')"

        try:
            results = self.make_request([query])
        except CouldNotRetrieveResult as e:
            return {"error" : str(e)}

        # Unpack result from multiple prompts
        results = results[0] if results else []
        # Take first result
        results = results[0] if results else {}
        return results

    def change_properties(self, id, input_properties):
        """! Function used by the core to change properties in the database

        Set dirty bit to 1 so embeddings are recalculated

        @param id: The id
        @param input_properties: The input properties
        """
        self.client.GremlinGraphManager.change_properties(id, input_properties)


if __name__ == "__main__":
    a = AzureCommunicationClient()
