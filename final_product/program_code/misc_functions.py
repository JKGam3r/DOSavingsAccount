# A collection of functions that don't fit into any other file

import datetime # Used to format a date
import os # Used for finding an absolute path

# Gives a month (in string format) based on the month number (such as 0=January, 11=December)
# Note that typically, 1=January, but list format dictates indexes start at 0
month_list = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]

# Pieces together a date, tested by verifying actual, current date (and format)
def format_date():
    # Information on the time of the function call
    current_time = datetime.datetime.now().timetuple()

    # Display hours with two digits
    hours = current_time[3] if current_time[3] > 9 else f"0{current_time[3]}"

    # Display minutes with two digits
    minutes = current_time[4] if current_time[4] > 9 else f"0{current_time[4]}"

    # Display either AM or PM
    part_of_day = "PM" if current_time[3] > 11 else "AM"

    # Display 12-hour clock hour time
    other_hour = current_time[3] - 12 if current_time[3] > 12 else current_time[3]
    if current_time[3] == 0:
        other_hour = 12
    corrected_other_hour = other_hour if other_hour > 9 else f"0{other_hour}"

    # Display 12-hour day view
    other_time = f"{corrected_other_hour}:{minutes} {part_of_day}"

    # Return the time
    return f"{current_time[2]} {month_list[current_time[1] - 1]} {current_time[0]} at {hours}:{minutes} ({other_time})\t"