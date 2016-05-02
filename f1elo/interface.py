from __future__ import print_function

import datetime
import sys

import dateutil.relativedelta
from f1elo.db import Session
from f1elo.elo import Elo
from f1elo.model import *
from sqlalchemy import MetaData


class Interface:

    def __init__(self, date=None):
        self.session = Session()
        self.date = date

    def init_db(self, force=False):
        from f1elo.model import Base
        if force:
            Base.metadata.drop_all(self.session.get_bind())
        Base.metadata.create_all(self.session.get_bind())

    def reset(self, date=None, _debug=False):
        if date is None:
            date = self.date

        query = self.session.query(Race)
        if date is not None:
            query = query.filter(Race.date > date)
        for race in query.all():
            race.ranked = False
            if _debug:
                print(race, file=sys.stderr)

        query = self.session.query(Ranking)
        if date is not None:
            query = query.filter(Ranking.rank_date > date)
        query.delete()

        self.session.commit()

        if date is not None:
            date += datetime.timedelta(1)

        self.date = date

        return

    def rate(self, date=None, _debug=False):
        if date is None:
            date = self.date
        if date is None:
            date = datetime.date.today()

        elo = Elo(self.session)
        race_query = self.session.query(Race).filter(Race.ranked == False)
        if date is not None:
            race_query = race_query.filter(Race.date <= date)
        races = race_query.order_by(Race.date, Race.id).all()

        for race in races:
            if _debug:
                print(race, file=sys.stderr)
                print('', file=sys.stderr)

            ranks = elo.rank_race(race)
            driver_ranks = {}
            for entry, rank in ranks.iteritems():
                if entry.result_group:
                    correction = rank / len(entry.drivers)
                    for driver in entry.drivers:
                        if driver not in driver_ranks:
                            driver_ranks[driver] = 0
                        driver_ranks[driver] += correction
            for driver, rank in driver_ranks.iteritems():
                ranking = Ranking()
                ranking.rank_date = race.date
                ranking.ranking = round(elo.get_ranking(driver, race.date) + rank, 2)
                self.session.add(ranking)
                driver.rankings.append(ranking)

            if _debug:
                podium_rating = 0
                podium_rating_after = 0
                rating_sum = 0
                rating_change_sum = 0
                for entry in sorted(race.entries):
                    old_rating = elo.get_entry_ranking(entry,
                                                       race.date - dateutil.relativedelta.relativedelta(days=1))
                    new_rating = elo.get_entry_ranking(entry)
                    rating_sum += old_rating
                    rating_change_sum += abs(new_rating - old_rating)
                    print(
                        entry,
                        old_rating,
                        new_rating,
                        file=sys.stderr)
                    if entry.result in ['1','2','3']:
                        podium_rating += old_rating
                        podium_rating_after += new_rating
                print('', file=sys.stderr)
                print('Podium rating: ', podium_rating, podium_rating_after, file=sys.stderr)
                print('Average rating: ', rating_sum / len(race.entries), file=sys.stderr)
                print('Average rating change: ', rating_change_sum / len(race.entries), file=sys.stderr)
                print('', file=sys.stderr)

            race.ranked = True
            date = race.date

        self.session.commit()

        self.date = date

        if self.date is not None:
            self.date += datetime.timedelta(1)

        return

    def fetch(self, date=None):
        if date is None:
            date = self.date
        if date is None:
            date = datetime.date.today()
            date += datetime.timedelta(1)

        one_year = dateutil.relativedelta.relativedelta(years=1)
        rankings = self.session.query(
            Ranking
        ).filter(
            Ranking.rank_date > (date - one_year)
        ).filter(
            Ranking.rank_date <= date
        ).all()

        drivers = {}
        for ranking in rankings:
            if ranking.driver not in drivers:
                drivers[ranking.driver] = ranking.driver.get_ranking(date)

        self.date = date

        return sorted(drivers.values(), key=lambda rank: rank.ranking, reverse=True)
