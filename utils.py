# python standard libraries
from os.path import join
import time



'''
A module to hold functions that may be used by multiple other modules

You may think that these are useless functions since they only have 1 line
You may be thinking "Why would I use iso_date() when I can just use time.strftime('%Y-%m-%d', time.localtime())?"

Answer:
    1. These are good for abstraction. iso_date() is more easily readable than time.strftime('%Y-%m-%d', time.localtime())
    2. If changes need to be made to this format (like if we wanted to change year from yyyy to just yy), then we would
       only need to edit iso_date() instead of editing every instance of time.strftime('%Y-%m-%d', time.localtime()) across
       multiple files
'''



def iso_date() -> str:
    '''
    Returns:
        str: the current date in iso 8601 format yyyy-mm-dd
    '''
    return time.strftime("%Y-%m-%d", time.localtime())



def unix_time() -> float:
    '''
    Returns:
        float: the time in seconds since the epoch (aka unix time)
    '''
    return time.time()



def display_date(date = time.localtime()) -> str:
    '''
    Args:
        date (time.struct_time, optional): the datetime to convert. defaults to the current time if no arg is provided.

    Returns:
        str: a "pretty" string representation of the current date like
             Monday June 09, 1969
    '''
    return time.strftime("%a %b %d, %Y", date)



def display_datetime() -> str:
    '''
    Returns:
        str: a "pretty" string representation of the current datetime like
             Sunday July 20, 1969 at 10:56 PM
    '''
    return time.strftime("%a %b %d, %Y at %I:%M %p", time.localtime())



def iso_to_display_date(iso: str) -> str:
    '''
    Converts an iso date to a "pretty" date

    Args:
        iso (str): date in iso 8601 format as returned by iso_date()

    Returns:
        str: "pretty" date as obtained from display_date()
    '''
    date = time.strptime(iso, "%Y-%m-%d")
    return display_date(date)



def directory(app_dir) -> str:
    '''
    Returns:
        str: the directory the calling module is in
    '''
    return join(app_dir, 'static')