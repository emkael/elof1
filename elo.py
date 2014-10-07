#!/usr/bin/env python
import argparse
import datetime

import dateutil.parser
import dateutil.relativedelta
from f1elo.db import Session
from f1elo.elo import Elo
from f1elo.model import *

session = Session()
elo = Elo(session)

parser = argparse.ArgumentParser(description='Ranks Formula One drivers using Elo rating')
parser.add_argument('command', metavar='COMMAND', nargs='?',
                    help='Action to execute against the database: print, reset or rate, print - prints the rankings for all drivers ranked in 12 months, reset - resets the rankings, rate - calculates the rankings',
                    default='print')
parser.add_argument('--date', help='Date for which the action should be executed. Print ratings for DATE, reset ratings all the way down to DATE or rank the races all the way up to DATE.')

arguments = parser.parse_args()
command = arguments.command.lower()
date = arguments.date
if date:
    date = dateutil.parser.parse(date).date()

one_day = datetime.timedelta(1)

if command == 'reset':
    query = session.query(Race)
    if date is not None:
        query = query.filter(Race.date > date)
    for race in query.all():
        race.ranked = False
    query = session.query(Ranking)
    if date is not None:
        query = query.filter(Ranking.rank_date > date)
    query.delete()
    if date is not None:
        date += one_day
elif command == 'rate':
    race_query = session.query(Race).filter(Race.ranked == False)
    if date is not None:
        race_query = race_query.filter(Race.date <= date)
    races = race_query.order_by(Race.date).all()

    for race in races:
        print race
        print

        ranks = elo.rank_race(race)
        driver_ranks = {}
        for entry, rank in ranks.iteritems():
            correction = rank / len(entry.drivers)
            for driver in entry.drivers:
                if not driver_ranks.has_key(driver):
                    driver_ranks[driver] = 0;
                driver_ranks[driver] += correction
        for driver, rank in driver_ranks.iteritems():
            ranking = Ranking()
            ranking.rank_date = race.date
            ranking.ranking = elo.get_ranking(driver, race.date) + rank
            session.add(ranking)
            driver.rankings.append(ranking)

        for entry in race.entries:
            print entry, elo.get_entry_ranking(entry, race.date), elo.get_entry_ranking(entry)
        print

        race.ranked = True
        date = race.date + one_day

if date is None:
    date = datetime.date.today()
    date += one_day

one_year = dateutil.relativedelta.relativedelta(years=1)
rankings = session.query(Ranking).filter(Ranking.rank_date > (date - one_year)).filter(Ranking.rank_date <= date).all()

if len(rankings):
    print 'Rankings for %s' % date

    drivers = {}
    for ranking in rankings:
        if not drivers.has_key(ranking.driver):
            drivers[ranking.driver] = ranking.driver.get_ranking(date)


    for rank in sorted(drivers.values(), key=lambda rank: rank.ranking, reverse=True):
        print rank
else:
    print 'No rankings for %s' % date

session.commit()
