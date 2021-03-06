#!/usr/bin/env python3

"""
Open terminal window with prompt to quickly enter text to save in Inbox. Best
used with global keyboard shortcut. Alternatively, if called with -c, will add
contents of clipboard to Inbox.
"""

# TODO: Fix pylint error: unable to import pygtd (but it works anyway...)

import argparse
import pyperclip
from pygtd import load_data, save_data, add_to_inbox, inbox_popup
from os import path
from time import time
from sys import argv

data = {}


def main():
    load_data()
    if argv[1] == '-c':
        add_to_inbox(pyperclip.paste())
    else:
        inbox_popup()


if __name__ == '__main__':
    main()
