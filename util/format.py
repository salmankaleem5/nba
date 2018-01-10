import datetime


def get_year_string(year):
    return str(year) + "-" + str(year + 1)[2:4]


# Convert PCTIMESTRING of the format MM:SS along with the quarter to absolute seconds into the game
# Returns pandas column
def convert_time(time, quarter):
    quarter.map(int)
    minutes = time.map(lambda x: x.split(':')[0]).map(int)
    seconds = time.map(lambda x: x.split(':')[1]).map(int)
    return ((quarter - 1) * 12 * 60) + ((12 * 60) - (minutes * 60) - seconds)
