import json, dateutil
from sqlalchemy import func
from itertools import combinations
from os import path

import __main__
from f1elo.model import *


class Elo:

    def __init__(self, session):
        self.session = session
        self.config = json.load(
            open(path.join(path.dirname(__main__.__file__), 'config', 'elo.json')))

    def get_ranking(self, driver, rank_date=None):
        rank = driver.get_ranking(rank_date)
        if rank:
            return rank.ranking
        return self.config['initial_ranking']

    def get_entry_ranking(self, entry, date=None):
        return sum([self.get_ranking(d, date) for d in entry.drivers]) / len(entry.drivers)

    def rank_race(self, race):
        race_disparity = self.config['disparity']['base_disparity']
        if self.config['disparity']['adjust']:
            recent_date = race.date - dateutil.relativedelta.relativedelta(months=3)
            recent_ratings = self.session.query(
                func.min(Ranking.ranking).label('min'),
                func.max(Ranking.ranking).label('max')
            ).filter(
                Ranking.rank_date >= recent_date
            ).group_by(
                Ranking._driver
            )
            changes_query = self.session.query(
                func.avg(
                    recent_ratings.subquery().columns.max - recent_ratings.subquery().columns.min
                )
            )
            recent_rank_change = changes_query.scalar()
            if not recent_rank_change:
                recent_rank_change = 0
            recent_rank_change = min(self.config['disparity']['base_rating_change'], recent_rank_change)
            race_disparity *= (2.5 + (self.config['disparity']['base_rating_change']/(recent_rank_change - 2.0 * self.config['disparity']['base_rating_change']))) * 0.5
        entries = race.entries
        entries_to_compare = []
        rankings = {}
        new_rankings = {}
        for e in entries:
            rankings[e] = self.get_entry_ranking(e, race.date)
            new_rankings[e] = 0.0
            if e.result_group:
                entries_to_compare.append(e)
        for c in combinations(entries_to_compare, 2):
            score = self.get_score(
                rankings[c[0]] - rankings[c[1]],
                self.get_outcome(c),
                self.get_importance(race,
                                    [rankings[c[0]],
                                     rankings[c[1]]]),
                race_disparity
            )
            new_rankings[c[0]] += score
            new_rankings[c[1]] -= score
        return new_rankings

    def get_importance(self, race, rankings):
        base_importance = self.config['importance'][race.type.code]
        min_rank = min(rankings)
        if min_rank < min(self.config['importance_threshold']):
            return base_importance
        if min_rank <= max(self.config['importance_threshold']):
            return base_importance * 0.75
        return base_importance / 2

    def get_outcome(self, entries):
        if entries[0].result_group < entries[1].result_group:
            return 1
        elif entries[0].result_group > entries[1].result_group:
            return 0
        return 0.5

    def get_score(self, difference, outcome, importance, disparity):
        return importance * (outcome - 1 / (1 + (10 ** (-difference / disparity))))
