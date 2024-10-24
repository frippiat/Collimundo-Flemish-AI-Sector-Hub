from pathlib import Path
import os
import time

# log to file
log_directory = os.path.join(Path(__file__).resolve().parent, "logs")
BOB = "2222"

ratings_file = os.path.join(log_directory, "ratings_CP_log.txt") 
def SAVE_RATING(info):
    ratings_log_(ratings_file, info)


ratings_log_file = os.path.join(log_directory, "ratings_CP_log.txt") 
def LOG_RATINGS(info):
    ratings_log_(ratings_log_file, info)


def ratings_log_(log_file, info):
    current_time = time.localtime()
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S", current_time)
    with open(ratings_log_file, "a") as log_file:
        log_file.write(timestamp + " : " + info + "\n")
