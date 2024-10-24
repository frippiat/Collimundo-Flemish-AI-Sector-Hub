from pathlib import Path
import os
import time

# log to file
log_directory = os.path.join(Path(__file__).resolve().parent, "logs")
BOB = "2222"

CP_request_file = os.path.join(log_directory, "CP_request_log.txt") 
def SAVE_CP_REQUEST(info):
    cp_request_log_(CP_request_file, info)


request_CP_log_file = os.path.join(log_directory, "CP_request_log.txt") 
def LOG_CP_REQUEST(info):
    cp_request_log_(request_CP_log_file, info)


def cp_request_log_(log_file, info):
    current_time = time.localtime()
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S", current_time)
    with open(request_CP_log_file, "a") as log_file:
        log_file.write(timestamp + " : " + info + "\n")
