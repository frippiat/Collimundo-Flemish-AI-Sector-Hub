
class NoConnectionToDatabase(Exception):
    """! Exception raised when no connection could be made to the database
    """
    "No connection could be made to the database"
    pass

class InvalidGremlinSyntax(Exception):
    """! Exception raised when the gremlin syntax is invalid
    """
    "Query contains invalid gremlin syntax"
    pass

class CouldNotRetrieveResult(Exception):
    """! Exception raised when the result could not be retrieved
    """
    def __init__(self, message):            
        super().__init__(message)

class NoValidOpenAIResult(Exception):
    """! Exception raised when the result from OpenAI is not valid
    """
    def __init__(self, message):            
        super().__init__(message)
