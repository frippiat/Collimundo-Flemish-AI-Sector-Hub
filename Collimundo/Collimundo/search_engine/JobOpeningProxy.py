try:
    from .JobOpeningCore import JobOpeningCore
except (ModuleNotFoundError, ImportError):
    from JobOpeningCore import JobOpeningCore


class JobOpeningProxy():
    """! Class used to guide the whole search process for job openings. This is a proxy class for the JobOpeningCore class.
    This class is used to communicate with the front end and the JobOpeningCore class.
    """

    def __init__(self, debug=False):
        self.JobOpeningCore = JobOpeningCore(self, debug=debug)
        self.result = None
        self.finished = False

    # function used by front end to submit a search query in string format to the job opening search engine
    def search(self, query):
        """! Function used by front end to submit a search query in string format to the job opening search engine

        @param query: The search query
        """
        print(f"Searching for {query}")
        self.finished = False
        self.JobOpeningCore.search(query)

    # function used by job opening core to set the right result in the proxy
    def set_result(self, result):
        """! Function used by job opening core to set the right result in the proxy

        @param result: The result
        """
        self.result = result

    # function used by job opening core to set the finished variable
    def set_finished(self, finished):
        """! Function used by job opening core to set the finished variable

        @param finished: The finished variable
        """
        self.finished = finished

    # function used by front end to get the result from the proxy
    def get_result(self):
        """! Function used by front end to get the result from the proxy

        @return: The result
        """
        return self.result

    # function used by front end to get the finished status from the proxy
    def get_finished(self):
        """! Function used by front end to get the finished status from the proxy

        @return: The finished status
        """
        return self.finished
