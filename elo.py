#!/usr/bin/env python
import argparse
import dateutil.parser

from f1elo.interface import Interface

parser = argparse.ArgumentParser(description='Ranks Formula One drivers using Elo rating')
parser.add_argument('command', metavar='COMMAND', nargs='?',
                    help='Action to execute against the database: print, reset or rate, print - prints the rankings for all drivers ranked in 12 months, reset - resets the rankings, rate - calculates the rankings',
                    default='print', choices=['print', 'rate', 'reset'])
parser.add_argument('--date', help='Date for which the action should be executed. Print ratings for DATE, reset ratings all the way down to DATE or rank the races all the way up to DATE.')
parser.add_argument('-v', help='Display verbose info on rating progress.', action='store_true')

arguments = parser.parse_args()
command = arguments.command.lower()
date = arguments.date
if date:
    date = dateutil.parser.parse(date).date()

interface = Interface(date)

if command == 'reset':
    interface.reset(_debug=arguments.v)
elif command == 'rate':
    interface.rate( _debug=arguments.v)

rankings = interface.fetch()

if len(rankings):
    print 'Rankings for %s' % interface.date
    for rank in rankings:
        print rank
else:
    print 'No rankings for %s' % interface.date
