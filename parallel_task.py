import requests

import multiprocessing as mp
import threading
import time
from threading import Thread

# The website I got the data from: https://data.cdc.gov/Foodborne-Waterborne-and-Related-Diseases/NORS/5xkq-dg7x/about_data
TOP_API_URL = "https://data.cdc.gov/resource/5xkq-dg7x.json"

class Request_thread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url
        self.response = None

    def get_response(self):
            return self.response
    
    def run(self):
        data = requests.get(self.url)

        if data.status_code == 200:
            self.response = data.json()
        else:
            self.response = None
            print(f"Error: {data.status_code}")

class Data_Info:
    def __init__(self, data):
        super().__init__()
        self._year = data.get("year", "Not Reported")
        self._month = data.get("month", "Not Reported")
        self._state = data.get("state", "Not Reported")
        self._transmission_mode = data.get("primary_mode", "Not Reported")
        self._name = data.get("etiology", "Not Reported")
        self._place = data.get("setting", "Not Reported")
        self._death = data.get("deaths", "Not Reported")

    def __str__(self):
        output  = f"Year                       : {self._year}\n"
        output += f"Month                      : {self._month}\n"
        output += f"State                      : {self._state}\n"
        output += f"Mode of transmission       : {self._transmission_mode}\n"
        output += f"Name of illness            : {self._name}\n"
        output += f"Environment of contraction : {self._place}\n"
        output += f"Number of deaths           : {self._death}\n"
        return output
    
    def get_year(self):
        return self._year
    
    def get_month(self):
        return self._month
    
    def get_state(self):
        return self._state
    
    def get_transmission_mode(self):
        return self._transmission_mode
    
    def get_name(self):
        return self._name
    
    def get_place(self):
        return self._place
    
    def get_death(self):
        return self._death

# This function will keep track of the most comon month on incident.
def comon_month(info, month_of_illness):
    if info._month != None:
        month_of_illness[int(info._month) - 1][1] += 1

def no_parallelism():
    request = Request_thread(f"{TOP_API_URL}")
    request.start()
    request.join()

    disease_info = request.get_response()

    total_deaths = 0
    month_of_illness = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0]]

    # If there is no data found then the program will tell the user so.
    if disease_info is None:
        print("No information found.")
        return
    
    for data_points in disease_info:
        info = Data_Info(data_points)
        comon_month(info, month_of_illness)

        # Checks to see if the data in death is the string "Not Reported", if it isn't then the data is converted to an int and added to 
        # the total number of deaths.
        if info._death != "Not Reported":
            total_deaths += int(info._death)
        
        print(info)
    
    # Finds the month with the highest number of infections
    most_comon_month = 0
    for set_of_data in month_of_illness:
        if month_of_illness[most_comon_month - 1][1] < set_of_data[1]:
            most_comon_month = set_of_data[0]

    print(f"Most comon month for infection: {most_comon_month}")
    print(f"Total deaths: {total_deaths}")

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

def parallel_function(data_lock, data_points, month_of_illness, total_deaths):
    info = Data_Info(data_points)
    comon_month(info, month_of_illness)

    # Checks to see if the data in death is the string "Not Reported", if it isn't then the data is converted to an int and added to 
    # the total number of deaths. The lock here is used to make sure that the data doesn't get mixed up with another thread.
    if info._death != "Not Reported":
        with data_lock:
            total_deaths += int(info._death)

    print(info)

# The program with parallelism
def with_parallelism():
    request = Request_thread(f"{TOP_API_URL}")
    request.start()
    request.join()

    disease_info = request.get_response()

    total_deaths = 0
    month_of_illness = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0]]

    # If there is no data found then the program will tell the user so.
    if disease_info is None:
        print("No information found.")
        return
    
    with parallel_semaphore:
        for data_points in disease_info:
            data_lock = threading.Lock()
            data_thread = Thread(target=parallel_function, args=(data_lock, data_points, month_of_illness, total_deaths))
            # thread_list.append(data_thread)
            data_thread.start()

    
    # Finds the month with the highest number of infections
    most_comon_month = 0
    for set_of_data in month_of_illness:
        if month_of_illness[most_comon_month - 1][1] < set_of_data[1]:
            most_comon_month = set_of_data[0]

    print(f"Most comon month for infection: {most_comon_month}")
    print(f"Total deaths: {total_deaths}")

# thread_list = []
MAX_SIZE = 10
parallel_semaphore = threading.Semaphore(MAX_SIZE)

start_time_nop = time.time()
no_parallelism()
stop_time_nop = time.time()

time.sleep(1)

start_time_withp = time.time()
with_parallelism()
# for threads in thread_list:
#     threads.join()
stop_time_withp = time.time()

time.sleep(1)

print(f"Time without parallelism: {(stop_time_nop - start_time_nop):.2f} seconds")

print(f"Time with parallelism: {(stop_time_withp - start_time_withp):.2f} seconds")
# print(f"Number of threads: {len(thread_list)}")