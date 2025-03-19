#!/usr/bin/env python3

"""
Gathers all the applications that include a `locale` dir and (re)generates Django translation messages.

Usage:
    $ ./make_all_messages.py
"""

import os
import sys


def make_all_messages():
    print("Generating Django translation messages for apps...")
    for entry in os.listdir("."):
        if not os.path.isdir(entry):
            continue
        os.chdir(entry)
        if os.path.exists("locale"):
            print(entry)
            os.system(f"python ..{os.path.sep}manage.py makemessages -a")  # nosec start_process_with_a_shell
        os.chdir(f"..{os.path.sep}")
    print("Done.")


if __name__ == "__main__":
    try:
        make_all_messages()
    except Exception as e:
        sys.exit(str(e))
    sys.exit()
