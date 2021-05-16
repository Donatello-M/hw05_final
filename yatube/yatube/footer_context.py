import datetime as dt


def current_year(request):
    year = dt.datetime.today().year
    return {
        'year': year,
    }
