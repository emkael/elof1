#!/usr/bin/env python
import argparse
import dateutil.parser
import sys

parser = argparse.ArgumentParser(description='Ranks Formula One drivers using Elo rating',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('command', metavar='COMMAND', nargs='?',
                    help="Action to execute against the database:\n"
                    "print - prints the rankings for all drivers ranked in 12 months,\n"
                    "reset - resets the rankings,\n"
                    "rate - calculates the rankings\n"
                    "init - init clean database for the application\n"
                    "Default value is 'print'.",
                    default='print', choices=['print', 'rate', 'reset', 'init'])
parser.add_argument('--date',
                    help='Date for which the action should be executed.\n'
                    'Print ratings for DATE,\n'
                    'reset ratings all the way down to DATE\n'
                    'or rank the races all the way up to DATE.')
parser.add_argument('--limit', help='Ranking list (display) cut-off point.', type=int)
parser.add_argument('-v', help='Display verbose info on rating progress to STDERR.', action='store_true')
parser.add_argument('--force', '-f', help='Force database initialization (for "init" command).', action='store_true')

arguments = parser.parse_args()

command = arguments.command.lower()

date = arguments.date
if date:
    date = dateutil.parser.parse(date).date()

from f1elo.interface import Interface
interface = Interface(date)

if command == 'reset':
    interface.reset(_debug=arguments.v)
elif command == 'rate':
    interface.rate( _debug=arguments.v)
elif command == 'init':
    interface.init_db(force=arguments.force)
    sys.exit(0)

rankings = interface.fetch()

if len(rankings):
    print 'Rankings for %s' % interface.date
    if arguments.limit:
        rankings = rankings[0:arguments.limit]
    for rank in rankings:
        print rank
else:
    print 'No rankings for %s' % interface.date
