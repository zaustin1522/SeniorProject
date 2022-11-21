#-----------------------------------------------------------------------------------------#

###########################################################################################
#   Defining Utility Methods for custom Log Messages
###########################################################################################

#-----------------------------------------------------------------------------------------#


import time


#-----------------------------------------------------------------------------------------#
def logmessage(type: str = "SYSTEM", msg: str = "no content"):
    print("[" + log_date_time_string() + "] :: [" + type + "] :: " + msg)

#-----------------------------------------------------------------------------------------#
def log_date_time_string():
    monthname = [None,
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    """Return the current time formatted for logging."""
    now = time.time()
    year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
    s = "%02d/%3s/%04d %02d:%02d:%02d" % (
            day, monthname[month], year, hh, mm, ss)
    return s
