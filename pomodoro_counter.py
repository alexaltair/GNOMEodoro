# This needs an apt install gir1.2-appindicator3-0.1

import csv
from datetime import date
import os
import signal

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import AppIndicator3

APP_INDICATOR_ID = 'pomodoro_counter'
INDICATOR = AppIndicator3.Indicator.new(
    APP_INDICATOR_ID,
    os.path.abspath('timer.svg'),
    AppIndicator3.IndicatorCategory.SYSTEM_SERVICES,
)

POM_FILE = '2021_pomodoros.csv'
poms_for_the_year = []

def main():
    with open(POM_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile)

        for row in reader:
            date = row[0]
            assert datetime_valid(date), "Row x column 0 is not a date. Instead it is x."
            poms = row[1]
            poms_for_the_year.append({
                'date': date,
                'poms': poms,
            })

    INDICATOR.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    update_poms_label()
    INDICATOR.set_menu(build_menu())
    Gtk.main()

def build_menu():
    menu = Gtk.Menu()

    item_increment = Gtk.MenuItem(label='Add one')
    item_increment.connect('activate', increment_poms)
    menu.append(item_increment)

    item_quit = Gtk.MenuItem(label='Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)

    menu.show_all()
    return menu

def increment_poms(_):
    global poms_for_the_year
    if poms_for_today()['poms'] is "":
        poms_for_today()['poms'] = "0"
    else:
        poms_for_today()['poms'] = str(int(poms_for_today()['poms']) + 1)

    with open(POM_FILE, 'w', newline='') as csvfile:
        # import pdb;pdb.set_trace()
        writer = csv.writer(csvfile)
        for pom_dict in poms_for_the_year:
            writer.writerow([pom_dict['date'], pom_dict['poms']])

    update_poms_label()

def quit(_):
    Gtk.main_quit()

def datetime_valid(string):
    try:
        date.fromisoformat(string)
    except ValueError:
        return False
    return True

def year_index_of_day():
    return date.today().timetuple().tm_yday - 1

def poms_for_today():
    poms = poms_for_the_year[year_index_of_day()]
    assert date.fromisoformat(poms['date']) == date.today(), "Date value from spreadsheet x does not match today's date."
    return poms

def update_poms_label():
    INDICATOR.set_label(
        poms_for_today()['poms'] + " poms",
        APP_INDICATOR_ID,
    )

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
