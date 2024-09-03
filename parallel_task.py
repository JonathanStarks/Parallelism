import requests
import multiprocessing as mp
import threading
import time
from threading import Thread

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
    
comon_data_nop = {
    "comon_month": 0,
    "most_cases_year": 0,
    "comon_year": 0,
    "comon_state": None,
    "most_cases_state": 0,
    "total_deaths": 0
    }

# This function interperets the API without using threads.
def no_parallelism():
    request = Request_thread(f"{TOP_API_URL}")
    request.start()
    request.join()

    disease_info = request.get_response()

    month_of_illness = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0]]
    year_of_illness = []
    state_of_illness = [["Alabama",0], ["Alaska",0], ["Arizona",0], ["Arkansas",0], ["California",0], ["Colorado",0], ["Conneticut",0], ["Delaware",0], ["Florida",0], ["Georgia",0], ["Hawaii",0], ["Idaho",0], ["Illinois",0], ["Indiana",0], ["Iowa",0], ["Kansas",0], ["Kentucky",0], ["Louisiana",0], ["Maine",0], ["Maryland",0], ["Massachusetts",0], ["Michigan",0], ["Minnesota",0], ["Mississippi",0], ["Missouri",0], ["Montana",0], ["Nebraska",0], ["Nevada",0], ["New Hampshire",0], ["New Jersey",0], ["New Mexico",0], ["New York",0], ["North Carolina",0], ["North Dakota",0], ["Ohio",0], ["Oklahoma",0], ["Oregon",0], ["Pennsylvania",0], ["Rhode Island",0], ["South Carolina",0], ["South Dakota",0], ["Tennessee",0], ["Texas",0], ["Utah",0], ["Vermont",0], ["Virginia",0], ["Washington",0], ["West Virginia",0], ["Wisconsin",0], ["Wyoming",0]]
    
    # If there is no data found then the program will tell the user so.
    if disease_info is None:
        print("No information found.")
        return
    
    for data_points in disease_info:
        info = Data_Info(data_points)

         # This statement will update the number of outbreaks that each month has.
        if info._month is not None:
            month_of_illness[int(info._month) - 1][1] += 1

        # This statement will update the number of outbreaks in each year.
        if info._year is not None:
            if len(year_of_illness) <= 0:
                year_of_illness.append([int(info._year), 1])
            elif year_of_illness[-1][0] == int(info._year):
                year_of_illness[-1][1] += 1
            else:
                year_of_illness.append([int(info._year), 1])
        # print(type(year_of_illness[len(year_of_illness) - 1][0]))
        # print(year_of_illness)

        # This statement will update the number of outbreaks in each state.
        if info._state is not None:
            if len(state_of_illness) <= 0:
                state_of_illness.append([info._state, 1])
            else:
                for state in state_of_illness:
                    if state[0] == info._state:
                        state[1] += 1
        # print(state_of_illness)


        # Checks to see if the data in death is the string "Not Reported", if it isn't then the data is converted to an int and added to 
        # the total number of deaths.
        if info._death != "Not Reported":
            comon_data_nop["total_deaths"] += int(info._death)

        # print(info)
    
    # Finds the month with the highest number of infections
    for set_of_data in month_of_illness:
        if month_of_illness[comon_data_nop["comon_month"] - 1][1] < set_of_data[1]:
            comon_data_nop["comon_month"] = set_of_data[0]
    
    # Finds the year with the highest number of cases
    for sets_of_data in year_of_illness:
        year, cases = sets_of_data
        if cases > comon_data_nop["most_cases_year"]:
            comon_data_nop["most_cases_year"] = cases
            comon_data_nop["comon_year"] = year

    # Finds the state with the highest number of cases
    for state_cases in state_of_illness:
        state_occur, cases = state_cases
        if cases > comon_data_nop["most_cases_state"]:
            comon_data_nop["most_cases_state"] = cases
            comon_data_nop["comon_state"] = state_occur

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

comon_data = {
    "comon_month": 0,
    "most_cases_year": 0,
    "comon_year": 0,
    "comon_state": None,
    "most_cases_state": 0,
    "total_deaths": 0
}

def month_outbreak(month_of_illness, comon_data, lock):
    # Finds the month with the highest number of infection.
    with lock:
        for set_of_data in month_of_illness:
            if month_of_illness[comon_data["comon_month"] - 1][1] < set_of_data[1]:
                comon_data["comon_month"] = set_of_data[0]

def year_outbreak(year_of_illness, comon_data, lock):
    # Finds the year with the highest number of cases.
    with lock:
        for sets_of_data in year_of_illness:
            year, cases = sets_of_data
            if cases > comon_data["most_cases_year"]:
                comon_data["most_cases_year"] = cases
                comon_data["comon_year"] = year

def state_outbreak(state_of_illness, comon_data, lock):
    # Finds the state with the highest number of cases.
    with lock:
        for state_cases in state_of_illness:
            state_occur, cases = state_cases
            if cases > comon_data["most_cases_state"]:
                comon_data["most_cases_state"] = cases
                comon_data["comon_state"] = state_occur


# The program with parallelism
def with_parallelism():
    request = Request_thread(f"{TOP_API_URL}")
    request.start()
    request.join()

    disease_info = request.get_response()

    year_of_illness = []
    month_of_illness = [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[11,0],[12,0]]
    state_of_illness = [["Alabama",0], ["Alaska",0], ["Arizona",0], ["Arkansas",0], ["California",0], ["Colorado",0], ["Conneticut",0], ["Delaware",0], ["Florida",0], ["Georgia",0], ["Hawaii",0], ["Idaho",0], ["Illinois",0], ["Indiana",0], ["Iowa",0], ["Kansas",0], ["Kentucky",0], ["Louisiana",0], ["Maine",0], ["Maryland",0], ["Massachusetts",0], ["Michigan",0], ["Minnesota",0], ["Mississippi",0], ["Missouri",0], ["Montana",0], ["Nebraska",0], ["Nevada",0], ["New Hampshire",0], ["New Jersey",0], ["New Mexico",0], ["New York",0], ["North Carolina",0], ["North Dakota",0], ["Ohio",0], ["Oklahoma",0], ["Oregon",0], ["Pennsylvania",0], ["Rhode Island",0], ["South Carolina",0], ["South Dakota",0], ["Tennessee",0], ["Texas",0], ["Utah",0], ["Vermont",0], ["Virginia",0], ["Washington",0], ["West Virginia",0], ["Wisconsin",0], ["Wyoming",0]]
    
    # If there is no data found then the program will tell the user so.
    if disease_info is None:
        print("No information found.")
        return
    
    for data_points in disease_info:
        info = Data_Info(data_points)

        # This statement will update the number of outbreaks that each month has.
        if info._month is not None:
            month_of_illness[int(info._month) - 1][1] += 1

        # This statement will update the number of outbreaks in each year.
        if info._year is not None:
            if len(year_of_illness) <= 0:
                year_of_illness.append([int(info._year), 1])
            elif year_of_illness[-1][0] == int(info._year):
                year_of_illness[-1][1] += 1
            else:
                year_of_illness.append([int(info._year), 1])

        # This statement will update the number of outbreaks in each state.
        if info._state is not None:
            if len(state_of_illness) <= 0:
                state_of_illness.append([info._state, 1])
            else:
                for state in state_of_illness:
                    if state[0] == info._state:
                        state[1] += 1

        # Checks to see if the data in death is the string "Not Reported", if it isn't then the data is converted to an int and added to 
        # the total number of deaths.
        if info._death != "Not Reported":
            comon_data["total_deaths"] += int(info._death)


    lock = threading.Lock()
    month_thread = threading.Thread(target=month_outbreak, args=(month_of_illness, comon_data, lock))
    year_thread = threading.Thread(target=year_outbreak, args=(year_of_illness, comon_data, lock))
    state_thread = threading.Thread(target=state_outbreak, args=(state_of_illness, comon_data, lock))

    #month
    month_thread.start()

    #year
    year_thread.start()

    #state
    state_thread.start()

    month_thread.join()
    year_thread.join()
    state_thread.join()


print("-----Without Parallelism-----")
start_time_nop = time.time()
no_parallelism()
stop_time_nop = time.time()
print(f"Most comon year for outbreak is {comon_data_nop['comon_year']} with {comon_data_nop['most_cases_year']} cases.")
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
print(f"Most common month for outbreak is {months[comon_data_nop['comon_month'] - 1]}")
print(f"Most comon state for outbreak is {comon_data_nop['comon_state']} with {comon_data_nop['most_cases_state']}")
print(f"Total deaths: {comon_data_nop['total_deaths']}")
print(f"Time taken: {(stop_time_nop - start_time_nop):.2f} seconds")

print()

print("-----With Parallelism-----")
start_time_withp = time.time()
with_parallelism()
stop_time_withp = time.time()
print(f"Most comon year for outbreak is {comon_data['comon_year']} with {comon_data['most_cases_year']} cases.")
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
print(f"Most common month for outbreak is {months[comon_data['comon_month'] - 1]}")
print(f"Most comon state for outbreak is {comon_data['comon_state']} with {comon_data['most_cases_state']}")
print(f"Total deaths: {comon_data['total_deaths']}")
print(f"Time taken: {(stop_time_withp - start_time_withp):.2f} seconds")

print()

print("-----Average Times From Twenty Runs-----")
# Finding the average time for not using threads
times_with_no_threads = []
time_to_be_averaged_nop = 0
for i in range(20):
    start_time_nop = time.time()
    with_parallelism()
    stop_time_nop = time.time()
    times_with_no_threads.append(stop_time_nop - start_time_nop)

for times in times_with_no_threads:
    time_to_be_averaged_nop += times

print(f"Average time for no threads: {(time_to_be_averaged_nop / len(times_with_no_threads)):.2f} seconds")

# Finding the average time using threads
times_with_threads = []
time_to_be_averaged_withp = 0
for i in range(20):
    start_time_withp = time.time()
    with_parallelism()
    stop_time_withp = time.time()
    times_with_threads.append(stop_time_withp - start_time_withp)

for times in times_with_threads:
    time_to_be_averaged_withp += times

print(f"Average time with using threads: {(time_to_be_averaged_withp / len(times_with_threads)):.2f} seconds")