#!/usr/bin/env python3

"""
Class-based version for possible refactor. Maybe will use ORM. For now, I think
I'll use shelf for storage.
"""

import argparse
import json
import pyperclip
import datetime
import re
import shelve
import jsonpickle
from os import path
from time import time, sleep
from sys import stdout, argv, exit
from dateutil import parser
from inspect import currentframe, getframeinfo
from pathlib import Path
from operator import attrgetter
from collections import deque
from math import floor
import pyrebase
import secrets
from quickstart import get_events, save_event
from copy import deepcopy
import pprint

# Ensure filepath for data files is in module directory regardless of cwd.
FILENAME = getframeinfo(currentframe()).filename
PARENT = Path(FILENAME).resolve().parent
DATA_FILE = PARENT / 'pygtd.json'
PICKLE_FILE = PARENT / 'pickle.json'

# Firebase
SERVICE_ACCOUNT_CREDENTIALS = PARENT / 'pygtd-7b396b5dc2be.json'

config = {
    "apiKey": secrets.apiKey,
    "authDomain": "pygtd-b8b3d.firebaseapp.co",
    "databaseURL": "https://pygtd-b8b3d.firebaseio.com",
    "storageBucket": "pygtd-b8b3d.appspot.com",
    "serviceAccount": SERVICE_ACCOUNT_CREDENTIALS
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()  # authenticate a user
user = auth.sign_in_with_email_and_password(
    secrets.email, secrets.password)
db = firebase.database()


def timedif(then):
    """Return time difference between now and Unix timestamp in seconds."""

    difsec = time() - then
    return round(difsec)


def confirm_date_parse():
    """Prompt user for date and confirm accuracy. Return datetime object.

    Allow user to enter date in any format. Confirm date has been parsed
    correctly before continuing.

    """
    ok = False
    while not ok:
        date = input("Date (and time, optional)\nAny format should work:\n> ")
        date = parser.parse(date)
        print("Date/Time: {}".format(str(date)))
        isok = input("Ok? (y/n)").lower()
        if 'y' in isok:
            ok = True
        else:
            print("Let's try again...")
    return date


def center_print(title, pad='*', size=80):
    """Print word in center of line surrounded by specified character.

    For printing titles. Ie:
    ******************************TITLE******************************

    """
    length = floor((size - len(title))/2)
    text = (pad * length) + title + (pad * length)
    if len(title) % 2 != 0:
        text += pad
    print(text)


def timer(seconds):
    """Display countdown for specified time."""

    # TODO: add alarm sound
    while True:
        try:
            print('              ', end='\r', flush=True)
            print('   ' + str(seconds), end='\r', flush=True)
            sleep(1)
            seconds -= 1
            if seconds < 0:
                break
        except KeyboardInterrupt:
            break
    print("Time's up!")


class Inbox():
    """Create Inbox container object.

    Stores collection of Inbox items and associated actions. Dequeue is used
    as most common operation will be FIFO processing of items.

    """

    def __init__(self, items={}):
        """Initialize queue for Inbox items."""

        self.items = items

    def add(self, text, created=None):
        """Add new Inbox item."""
        created = created or str(time()).replace('.', '-')
        item = {
            'text': text,
        }
        self.items[created] = item

    def print(self):
        """Print Inbox item."""

        for _, item in self.items.items():
            print(item['text'])

    def quickadd(self):
        """Display a prompt to add new Inbox item.

        For use with global keyboard shortcut to create popup terminal for rapid
        task entry.
        """
        text = input('INBOX> ')
        self.add(text)

    def paste(self):
        """Save clipboard contents as new Inbox item."""
        self.add(pyperclip.paste())


class NextActionList():
    """Create Next Action container."""

    def __init__(self, items={}):
        """Initialize list for Next Actions."""
        self.items = items

    def add(self, text, created):
        created = created or str(time()).replace('.', '-')
        newitem = {
            'text': text
        }
        self.items[created] = newitem

    def print(self):
        """Print Next Action."""
        for _, item in self.items.items():
            print(item['text'])

    def i_new_item(self, created=None):
        """Create new item with interactive prompt."""
        print("Next Action: What's the next thing you need to do to move toward "
              + "the desired outcome?\nVisualize yourself doing it and describe it "
              + "in a sentence. Be specific. Ie not 'set up meeting', but 'pick up "
              + "the phone and call X'.")
        text = input("NEXT ACTION> ")
        self.add(text, created)
        print('New item added to Next Actions list.')


class WaitingForList():
    """Create Waiting For item container."""

    def __init__(self, items={}):
        """Initialize list for Waiting For items."""
        self.items = items

    def add(self, text, who=None, due=None, created=None):
        created = created or str(time()).replace('.', '-')
        try:
            due = due.isoformat()
        except TypeError:
            pass
        newitem = {
            'text': text,
            'who': who,
            'due': due,
        }
        self.items[created] = newitem

    def print(self):
        """Print Waiting For items."""

        today = datetime.datetime.today()
        for _, item in self.items.items():
            date = parser.parse(item['due'])
            days = (date - today).days if date else None
            text = '...' + item['text']
            if item['who']:
                text += ' from ' + item['who']
            if days:
                text += ' in ' + str(days) + ' days'
            print(text)

    def i_new_item(self, created=None):
        """Create new item with interactive prompts."""

        print('Who are you waiting on to do this? (Press Enter to skip.)')
        who = input('> ')
        print('What are you waiting for?')
        text = input('> ')
        print('When do you expect it to happen?')
        due = confirm_date_parse()
        self.add(text, who, due, created)
        print('New item added to Waiting For list.')


class ProjectList():
    """Create container for Project items."""

    def __init__(self, items={}):
        """Initialize ProjectList."""
        self.items = items

    def add(self, text, title=None, created=None, next_actions=[]):
        created = created or str(time()).replace('.', '-')
        newitem = {
            'text': text,
            'title': title,
            'next_actions': next_actions
        }
        self.items.append(newitem)

    def print(self):
        for _, item in self.items.items():
            print('[{}] {}'.format(item['title'], item['text']))
            # TODO: print next action

    def i_new_item(self, created=None):
        """Interactively create new item."""

        text = input("Project: What's the desired outcome? What are you committed "
                     + "to accomplishing or finishing about this? What would 'done'"
                     + " look like?\n> ")
        title = input("Short name: ")
        self.add(text, title, created)
        print('New Project added to Projects list.')


class MaybeSomedayList():
    """Container for MaybeSomeday items."""

    def __init__(self, items={}):
        self.items = items

    def add(self, text, created=None):
        created = created or str(time()).replace('.', '-')
        newitem = {
            'text': text,
        }
        self.items[created] = newitem

    def print(self):
        for _, item in self.items.items():
            print(item['text'])


class Calendar():
    """Create container for Calendar items."""

    def __init__(self, items=[]):
        self.items = items

    def add(self, item):
        self.items.append(item)

    def i_new_item(self, created=None):
        """Interactively create new Calendar item in Google Calendar.

        If no time is entered or time is 12:00AM, will assume all-day event.
        Otherwise, a one-hour-long event will be created.
        """

        text = input("Describe scheduled item:\n> ")
        ok = False
        # Use dateutil to parse any date input, such june 2, tues, next week,
        # etc. Confirm parse was accurate before continuing.
        while not ok:
            when = input(
                "Date (and time, optional)\nAny format should work:\n> ")
            when = parser.parse(when)
            print("Date/Time: {}".format(when.strftime('%c')))
            isok = input("Ok? (y/n)").lower()
            if 'y' in isok:
                ok = True
        if not when.strftime('%I:%M%p') == '12:00AM':
            end = when + datetime.timedelta(hours=1)
        else:
            end = when + datetime.timedelta(day=1)
        save_event(when, end, text)
        print('New item added to Calendar.')

    def print_upcoming(self, period=30):
        """Print Calendar items.

        Print all future calendar items within given number of days, the
        date/time at which they occur, and the time between now and then.

        """
        for item in self.items:
            # Google Calendar may give start and end times with key 'date' or
            # 'dateTime', depending on how event is entered.
            try:
                date = parser.parse(item['start']['date'])
            except KeyError:
                date = parser.parse(item['start']['dateTime'])
            try:
                today = datetime.datetime.today()
                delta = date - today
            except TypeError:
                today = datetime.datetime.now(datetime.timezone.utc)
                delta = date - today
            days = delta.days
            # only print dates that are not in the past and in specified range
            if days <= period and date >= today:
                dates = date.strftime('%a, %b %d')
                times = date.strftime('%I:%M%p')
                # If time in datetime object is 00:00, assume specific time was
                # not entered or desired.
                if not times == '12:00AM':
                    dates += ' ' + times
                hours = round(delta.seconds / 3600)
                print('{{{}}} {} ({} days, {} hours)'.format(
                    dates,
                    item['summary'],
                    days,
                    hours
                ))
        # TODO: test if date is within days or less in the future


class CompletedItemList():
    """Create container for completed items.

    Completed items can be of any (GTD list item) type.

    """

    def __init__(self, items={}):
        self.items = items

    def add(self, text, completed, created=None):
        created = created or str(time()).replace('.', '-')
        newitem = {
            'text': text,
            'completed': completed,
        }
        self.items[created] = newitem

    def print(self):
        for _, item in self.items.items():
            print(item['text'])


class GTD():
    """Create main program object.

    This object stores program data, and is responsible for saving and loading,
    importing and exporting, for handling interactions between container
    objects, etc.

    """

    def __init__(self):
        """Initialize dictionary to store program data."""
        self.d = {
            'inbox': Inbox(),
            'calendar': Calendar(),
            'next_actions': NextActionList(),
            'waiting_for': WaitingForList(),
            'projects': ProjectList(),
            'maybe_someday': MaybeSomedayList(),
            'completed_items': CompletedItemList()
        }

    def fb_export(self):
        """Save all data to Firebase.

        Overwrite each node (inbox, etc) with current data so deletions will be
        reflected. Assumes all current has already been loaded and any changes
        between database and current app data (including deletions) are
        intentional. Otherwise data might be deleted!

        """
        db.child('inbox').set(self.d['inbox'].items, user['idToken'])
        db.child('next_actions').set(
            self.d['next_actions'].items, user['idToken'])
        db.child('waiting_for').set(
            self.d['waiting_for'].items, user['idToken'])
        db.child('projects').set(self.d['projects'].items, user['idToken'])
        db.child('maybe_someday').set(
            self.d['maybe_someday'].items, user['idToken'])
        db.child('completed_items').set(
            self.d['completed_items'].items, user['idToken'])

        calendar = {}
        for item in self.d['calendar'].items:
            created = (parser.parse(
                item['created']) - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
            id = str(created).replace('.', '-')
            record = item
            calendar[id] = record
        db.child('calendar').set(calendar, user['idToken'])

    def fb_import(self):
        """Load all data from Firebase."""

        data = db.get(user['idToken']).val()
        try:
            self.d['inbox'].items = deepcopy(data['inbox'])
        except KeyError:
            pass
        try:
            self.d['next_actions'].items = deepcopy(data['next_actions'])
        except KeyError:
            pass
        try:
            self.d['waiting_for'].items = deepcopy(data['waiting_for'])
        except KeyError:
            pass
        try:
            self.d['projects'].items = deepcopy(data['projects'])
        except KeyError:
            pass
        try:
            self.d['maybe_someday'].items = deepcopy(data['maybe_someday'])
        except KeyError:
            pass
        try:
            self.d['completed_items'].items = deepcopy(data['completed_items'])
        except KeyError:
            pass

        # Import from Google calendar
        self.d['calendar'].items = get_events(10)

    def print_overview(self):
        """Call the print methods for container objects."""

        center_print('INBOX')
        self.d['inbox'].print()
        center_print('CALENDAR')
        self.d['calendar'].print_upcoming()
        center_print('NEXT ACTIONS')
        self.d['next_actions'].print()
        center_print('WAITING FOR')
        self.d['waiting_for'].print()
        center_print('PROJECTS')
        self.d['projects'].print()
        print()

    def process_inbox(self):
        """Display interactive prompts for user to process inbox items."""

        # FIFO. For each item, the user will be guided
        # by interactive prompts to create a new item based on inbox item. New
        # item will be given same timestamp as the inbox item. (Conceptually, the
        # item is being 'moved' or 'changed'.) When item is successfully
        # processed, it will be dequeued (removed), and loop will continue with
        # next (now first) item in queue. Loop until no items are left.

        d = self.d['inbox'].items
        inbox = deque(d.keys())
        while len(inbox):
            self.fb_export()
            key = inbox[0]
            # Use correct singular/plural form.
            item_items = 'items' if len(inbox) > 2 else 'item'
            print(f"\nProcess Item ({len(inbox)} {item_items} left)")
            print('\n', d[key]['text'], '\n')
            actionable = input("(a) Add to Next Actions\n"
                               + "(d) Do it now in 2 minutes\n"
                               + "(c) Schedule it -- add to Calendar\n"
                               + "(w) Add to Waiting For list\n"
                               + "(p) Add to Projects list\n"
                               + "(s) Add to Someday/Maybe\n"
                               + "(r) Add to Reference\n"
                               + "(t) Already done/Trash\n"
                               + "> ").lower()
            if 'a' in actionable:
                # Create new Next Action then delete Inbox item
                self.d['next_actions'].i_new_item(key)
                del d[inbox.popleft()]
                continue
            elif 'd' in actionable:
                # Complete task now in 2 minutes
                print("Do it now!")
                input("Press any key to start 2 min timer...")
                timer(120)
                done = input("Done? (y/n): ").lower()
                if 'y' in done:
                    d[key].completed = datetime.datetime.now().isoformat()
                    self.d['completed'][key] = d[key]
                    del d[inbox.popleft()]
                else:
                    continue  # repeat loop with same item
            elif 'c' in actionable:
                # Create new Calendar item
                self.d['calendar'].i_new_item(key)
                del d[inbox.popleft()]
                continue
            elif 'w' in actionable:
                # Create new Waiting For item
                self.d['waiting_for'].i_new_item(key)
                del d[inbox.popleft()]
                continue
            elif 'p' in actionable:
                # Create new Project
                self.d['projects'].i_new_item(key)
                del d[inbox.popleft()]
                continue
            elif 's' in actionable:
                # save item in SomedayMaybe for future consideration
                self.d['maybe_someday'].add(d[key]['text'], key)
                del d[inbox.popleft()]
                continue
            elif 'r' in actionable:
                # TODO: add reference list
                print('Not implemented')
                continue
            elif 't' in actionable:
                # delete item
                del d[inbox.popleft()]
                print('Item deleted.')
                continue
            else:
                print('Invalid input')

    def update_list(self, which):
        """Lists collection with prompt to delete/complete/etc."""
        items = self.d[which].items
        while True:
            # print each action along with its index
            title = which.replace('_', ' ').title()
            print('\n', title)
            for i, item in enumerate(items):
                print('  ' + str(i) + ' ' + item.text)
            print(
                'Enter number (if appropriate) followed by command [ie 1 d, 5t]:')
            print('(#d)one, (#t)rash, (#e)dit, (q)uit')
            choice = input('> ').lower()

            # parse input for command and/or index
            re_num = re.compile(r'\d*')
            re_char = re.compile('[dteq]')
            try:
                index = int(re_num.search(choice).group())
            except (AttributeError, ValueError):
                index = None
            try:
                command = re_char.search(choice).group()
            except AttributeError:
                command = None

            if not command:
                print('Invalid input!')
                continue

            if command == 'q':
                print('Goodbye!')
                break
            elif not index and index != 0:
                print('You must enter a number to specify target.')
                continue

            if index >= len(items):
                print('Value out of range.')
                continue

            if command == 't':
                print('Delete task: ' + items[index].text)
                confdelete = input('(y/n)').lower()
                if 'y' in confdelete:
                    items.pop(index)
                    print('Item deleted.')
                else:
                    print('Delete aborted.')
                    continue
            elif command == 'd':
                items[index].completed = datetime.datetime.now()
                self.d['completed_items'].items.append(items.pop(index))
                print('Item marked complete and moved to Completed Items list.')
                continue
            elif command == 'e':
                print('Not implimented')
                continue


def main():
    # only one argument is meant to be used at a time, but you could, say,
    # add an inbox item and view the lists at the same time if you wanted to

    # TODO: handle inappropriate option combinations

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-i',
        '--inbox',
        nargs='+',
        action='store',
        help='Add text to new Inbox item.'
    )
    group.add_argument(
        '-o',
        '--overview',
        action='store_true',
        help='Print lists to terminal.'
    )
    group.add_argument(
        '-P',
        '--paste',
        action='store_true',
        help='Adds contents of clipboard as new Inbox item.'
    )
    group.add_argument(
        '-q',
        '--quick-add',
        action='store_true',
        dest='quick',
        help='Create Inbox prompt for task entry. For use with global keyboard '
        + 'shortcut.'
    )
    group.add_argument(
        '-u',
        '--update-list',
        action='store',
        dest='update_list',
        nargs='?',
        help='Displays Next Actions and prompts user to delete/mark complete, '
        + 'etc.'
    )
    group.add_argument(
        '-d',
        '--process-inbox',
        action='store_true',
        dest='process_inbox',
        help='Process Inbox items.'
    )
    args = parser.parse_args()

    # instantiate object responsible for data
    gtd = GTD()
    # Inbox now adds directly to Firebase before loading data to save time.
    # Item will be in app data next time data is loaded from Firebase.
    if args.inbox:  # -i, --inbox
        # add text entered at CLI to inbox
        text = ' '.join(args.inbox)
        gtd.d['inbox'].add(text)
        print('"{}" added to inbox.'.format(text))
        return True
    if args.paste:  # -P, --paste
        # add clipboard contents to inbox
        gtd.d['inbox'].paste()
        return True
    if args.quick:
        # show Inbox prompt. For use with global keyboard shortcut.
        gtd.d['inbox'].quickadd()
        return True

    # load data
    gtd.fb_import()

    if args.overview:  # -o, --overview
        # print lists
        gtd.print_overview()
    if args.update_list:
        s = args.update_list[0].lower()
        if s[0] == 'i':
            which = 'inbox'
        elif s[0] == 'n':
            which = 'next_actions'
        elif s[0] == 'w':
            which = 'waiting_for'
        elif s[0] == 'p':
            which = 'projects'
        elif s[0] == 'm':
            which = 'maybe_someday'
        elif s[0] == 'c':
            which = 'calendar'
        gtd.update_list(which)
    if args.process_inbox:
        gtd.process_inbox()

    # save data to file
    # gtd.d['waiting_for'].items.append({
    #     "created": 1527184756.2047727,
    #     "text": "affidavit",
    #     "due": "2018-06-08 00:00:00",
    #     "who": "PenFed"
    # })
    gtd.fb_export()


if __name__ == '__main__':
    main()
