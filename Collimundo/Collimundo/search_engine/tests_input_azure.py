# own imports
import json

try:
    from .AzureCommunication import AzureCommunication
    from .CustomGremlinQueries import CustomGremlinQueries
    from .QuerySyntaxChecker import QuerySyntaxChecker
except (ModuleNotFoundError, ImportError):
    from AzureCommunication import AzureCommunication
    from CustomGremlinQueries import CustomGremlinQueries
    from QuerySyntaxChecker import QuerySyntaxChecker

# create test Proxy
azure_connection = AzureCommunication(True)
syntaxChecker = QuerySyntaxChecker(True)
customQueries = CustomGremlinQueries(azure_connection, True)


# function to input test data
def test_function_input():
    """! Function used to test the input of the proxy
    """
    print("start inputting - enter 'stop' to stop")
    inp = input("\n> ")
    while inp != "stop":
        # inp = syntaxChecker.check(inp)
        # res = azure_connection.make_request([inp])
        # if len(res) == 0:
        #     print( "\n NO RESULTS \n")
        # else:
        #     print("result:")
        #     for i, r in enumerate(res[0]):
        #         print(f"\n\n------------ Result {i}\n")
        #         print(json.dumps(r, indent=4))
        res = customQueries.extract_companies_and_connected(inp)
        print(json.dumps(res, indent=4))
        inp = input("\n> ")


test_function_input()
