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
poms_for_the_year: list

def main():
    global poms_for_the_year
    with open(POM_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile)

        def dictify_csv(row_list):
            # This will throw_list an error if it's not a date, and thus serves as a validation
            date.fromisoformat(row_list[0])
            assert (row_list[1] == "") or (0 <= int(row_list[1]))
            return {'date': row_list[0], 'poms': row_list[1]}

        poms_for_the_year = [dictify_csv(row) for row in reader]

    INDICATOR.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    update_poms_label()
    INDICATOR.set_menu(build_menu())
    Gtk.main()

def build_menu():
    menu = Gtk.Menu()

    item_increment = Gtk.MenuItem(label='Add one')
    item_increment.connect('activate', increment_poms)
    menu.append(item_increment)

    item_decrement = Gtk.MenuItem(label='Subtract one')
    item_decrement.connect('activate', decrement_poms)
    menu.append(item_decrement)

    item_sync = Gtk.MenuItem(label='Sync')
    item_sync.connect('activate', sync)
    menu.append(item_sync)

    item_quit = Gtk.MenuItem(label='Quit')
    item_quit.connect('activate', Gtk.main_quit)
    menu.append(item_quit)

    menu.show_all()
    return menu

def increment_poms(_):
    if poms_for_today()['poms'] == "":
        poms_for_today()['poms'] = "1"
    else:
        poms_for_today()['poms'] = str(int(poms_for_today()['poms']) + 1)

    sync()

def decrement_poms(_):
    if poms_for_today()['poms'] == "":
        poms_for_today()['poms'] = "0"
    elif poms_for_today()['poms'] == "0":
        return  # Can't be less than zero
    else:
        poms_for_today()['poms'] = str(int(poms_for_today()['poms']) - 1)

    sync()

def sync(*_):
    update_csv()
    update_poms_label()

def update_csv():
    with open(POM_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for pom_dict in poms_for_the_year:
            writer.writerow([pom_dict['date'], pom_dict['poms']])

def update_poms_label():
    if poms_for_today()['poms'] == "":
        poms_for_today()['poms'] = "0"

    INDICATOR.set_label(
        " " + poms_for_today()['poms'],
        APP_INDICATOR_ID,
    )

def year_index_of_day():
    return date.today().timetuple().tm_yday - 1

def poms_for_today():
    poms = poms_for_the_year[year_index_of_day()]
    err_str = f'Date value from spreadsheet "{poms["date"]}" does not match today\'s date ({date.today()}).'
    assert date.fromisoformat(poms['date']) == date.today(), err_str
    return poms

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
