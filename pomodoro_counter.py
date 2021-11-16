#!/usr/bin/env python3

# This needs an apt install gir1.2-appindicator3-0.1
import csv
from datetime import date, datetime
import os
import pathlib
import signal

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import AppIndicator3

APP_INDICATOR_ID = 'pomodoro_counter'
DIR_PATH = str(pathlib.Path(__file__).parent.resolve())
INDICATOR = AppIndicator3.Indicator.new(
    APP_INDICATOR_ID,
    os.path.join(DIR_PATH, 'timer.svg'),
    AppIndicator3.IndicatorCategory.SYSTEM_SERVICES,
)

POM_FILE = os.path.join(DIR_PATH, '2021_pomodoros.csv')
poms_for_the_year: list
stats_items = {}

def main():
    global poms_for_the_year
    with open(POM_FILE, newline='') as csvfile:
        reader = csv.reader(csvfile)

        def dictify_csv(row_list):
            # This will throw_list an error if it's not a date, and thus serves as a validation
            date.fromisoformat(row_list[0])
            assert (row_list[1] == "") or (0 <= int(row_list[1]))
            return {'date': row_list[0], 'poms': row_list[1]}

        poms_for_the_year = list(map(dictify_csv, reader))

    INDICATOR.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    update_poms_label()
    INDICATOR.set_menu(build_menu())
    Gtk.main()

def build_menu():
    menu = Gtk.Menu()

    item_increment = Gtk.MenuItem(label='+1')
    item_increment.connect('activate', increment_poms)
    menu.append(item_increment)

    item_decrement = Gtk.MenuItem(label='-1')
    item_decrement.connect('activate', decrement_poms)
    menu.append(item_decrement)

    item_sync = Gtk.MenuItem(label='Sync')
    item_sync.connect('activate', sync)
    menu.append(item_sync)


    item_timestamp = Gtk.MenuItem(label="No poms recorded yet")
    item_timestamp.set_sensitive(False)
    stats_items["timestamp"] = item_timestamp
    menu.append(item_timestamp)

    item_week_average = Gtk.MenuItem()
    item_week_average.set_sensitive(False)
    stats_items["week_average"] = item_week_average
    update_week_average()
    menu.append(item_week_average)

    item_year_average = Gtk.MenuItem()
    item_year_average.set_sensitive(False)
    stats_items["year_average"] = item_year_average
    update_year_average()
    menu.append(item_year_average)


    item_quit = Gtk.MenuItem(label='Quit')
    item_quit.connect('activate', Gtk.main_quit)
    menu.append(item_quit)

    menu.show_all()
    return menu

def update_timestamp():
    stats_items["timestamp"].set_label("Last pom: " + datetime.now().strftime("%b %d %H:%M"))

def increment_poms(_):
    if poms_for_today()['poms'] == "":
        poms_for_today()['poms'] = "1"
    else:
        poms_for_today()['poms'] = str(int(poms_for_today()['poms']) + 1)

    update_timestamp()
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
    update_week_average()
    update_year_average()

def update_csv():
    with open(POM_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for day in poms_for_the_year:
            writer.writerow([day['date'], day['poms']])

def update_poms_label():
    if poms_for_today()['poms'] == "":
        poms_for_today()['poms'] = "0"

    INDICATOR.set_label(
        " " + poms_for_today()['poms'],
        APP_INDICATOR_ID,
    )

def update_week_average():
    stats_items["week_average"].set_label("7-day avg: " + "{:.3f}".format(week_average()))

def update_year_average():
    stats_items["year_average"].set_label("2021 avg: " + "{:.4f}".format(year_average()))

def week_average():
    last_week = poms_for_the_year[year_index_of_day()-6:year_index_of_day()+1]
    return sum(map((lambda day: int(day['poms'])), last_week))/7

def year_average():
    days_with_poms = list(filter((lambda day: day['poms'] != ""), poms_for_the_year))
    return sum(map((lambda day: int(day['poms'])), days_with_poms))/len(days_with_poms)

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
