# dependencies
from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory

# local modules
import constants
import db_handler as dbh
import utils



APP = Flask(__name__)



@APP.route('/')
def home_page():
    '''
    Shows how many people are currently inside the building and how much traffic there is (for the day)
    '''
    db = dbh.DB_Handler(constants.DB_FILE)
    record = db.get_record(utils.iso_date())
    if not record:
        return render_template('dne.html', date=utils.display_date())

    data = {
        'datetime': utils.display_datetime(),
        'inside': record['ingress'] - record['egress'],
        'entrants': max(record['ingress'], record['egress'])
    }
    return render_template('home.html', data=data, base_url=request.url_root)



@APP.route('/favicon.ico')
def favicon():
    '''
    Serves GET favicon requests
    Favicons are the icons that show up in your browser's tab.
    For the purposes of this project, a favicon is not needed, so a blank one is used.

    Note:
        This function is required because browsers will try to access '{base_url}/favicon.ico'
        and without this function, the request will automatically go to the date_page() function
        where things will get messed up.
    '''
    return send_from_directory(utils.directory(APP.root_path), 'favicon.ico')



@APP.route('/<date>')
def date_page(date: str):
    '''
    Shows how many people entered, how many exited, and how much traffic there were

    Args:
        date (str): must be iso 8601 format (yyyy-mm-dd)
    '''
    if date == 'favicon.ico':
        return

    db = dbh.DB_Handler(constants.DB_FILE)
    data = db.get_record(date)
    if not data:
        return render_template('dne.html', date=utils.iso_to_display_date(date))

    data['display_date'] = utils.iso_to_display_date(data['date'])
    data['entrants'] = max(data['ingress'], data['egress'])
    return render_template('date.html', data=data, base_url=request.url_root)



@APP.route('/index')
def index_page():
    '''
    Shows all the dates for which data exists (ie. in the database)
    And gives the link to the webpage to view that data
    '''
    db = dbh.DB_Handler(constants.DB_FILE)
    dates = db.get_dates()
    for d in dates:
        d['display_date'] = utils.iso_to_display_date(d['date'])
    return render_template('index.html', dates=dates, base_url=request.url_root)



if __name__ == '__main__':
    APP.run(host='0.0.0.0')     # host='0.0.0.0' allows the web page to be discoverable to anyone on the same network