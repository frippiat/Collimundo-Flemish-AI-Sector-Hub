from pathlib import Path
import os
import time

# log to file
log_directory = os.path.join(Path(__file__).resolve().parent, "logs")
BOB = "2222"

votes_file = os.path.join(log_directory, "search_log.txt") 
def SAVE_VOTE(info):
    """! Save the vote in the log file
    @param info: the information to save
    """
    log_(votes_file, info)


search_log_file = os.path.join(log_directory, "search_log.txt") 
def LOG_SEARCH(info):
    """! Log the search query
    @param info: the information to save
    """
    log_(search_log_file, info)


def log_(log_file, info):
    """! Log the information to the log file
    @param log_file: the log file to write to
    @param info: the information to save
    """
    current_time = time.localtime()
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S", current_time)
    with open(search_log_file, "a") as log_file:
        log_file.write(timestamp + " : " + info + "\n")
