import datetime


def get_year_string(year):
    return str(year) + "-" + str(year + 1)[2:4]


# Convert PCTIMESTRING of the format MM:SS along with the quarter to absolute seconds into the game
# Returns pandas column
def convert_time(time, quarter):
    quarter.map(int)
    minutes = time.map(lambda x: x.split(':')[0]).map(int)
    seconds = time.map(lambda x: x.split(':')[1]).map(int)
    time_elapsed = (minutes * 60) + seconds
    previous_time = quarter.map(lambda x: ((x - 1) * 720) if x <= 4 else (2880 + ((x-5) * 300)))
    quarter_length = quarter.map(lambda x: 720 if x <= 4 else 300)
    return previous_time + (quarter_length - time_elapsed)
