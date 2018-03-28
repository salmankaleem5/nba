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


def get_name_part(name):
    special_names = {
        'LeBron James': 'LeBron',
        'Draymond Green': 'Draymond',
        'Chris Paul': 'CP3',
        'Kemba Walker': 'Kemba',
        'DeAndre Jordan': 'DJ',
        'Isaiah Thomas': 'IT',
        'Gerald Wallace': 'G Wallace',
        'Taj Gibson': 'T. Gibson',
        'Terrence Jones': 'T Jones',
        'Wesley Matthew': 'W Matthews',
        'Jeff Green': 'J Green',
        'Brandon Jennings': 'B Jennings'
    }

    if len(name.split(',')) > 1:
        name = name.split(', ')[1] + ' ' + name.split(', ')[0]

    if name in special_names:
        return special_names[name]
    elif len(name.split(' ')) < 2:
        return name
    else:
        return name.split(' ')[1]


def get_display_name(name_col, year_col):
    year_part = year_col.apply(lambda x: '\'' + x.split('-')[1])
    name_part = name_col.apply(lambda x: get_name_part(x))
    return name_part + ' ' + year_part
