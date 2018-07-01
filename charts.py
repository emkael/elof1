import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy.sql import text
from f1elo.db import Session
from itertools import izip
from dateutil import rrule, relativedelta
from datetime import date
import unicodecsv, collections, sys

session = Session()
engine = session.get_bind()
connection = engine.connect()

def fetch_raw():
    raw_queries = {
    'championship-races': '''
    SELECT CONCAT(race, ' (', date, ')') FROM races WHERE _type = 4
    ''',
    'all-time-top-peak': '''
    SELECT drivers.driver,
    rankings.ranking,
    rankings.rank_date
    FROM rankings
    INNER JOIN (
    SELECT MAX(ranking) ranking, _driver FROM rankings
    GROUP BY _driver
    ) r ON r.ranking=rankings.ranking AND r._driver=rankings._driver
    JOIN drivers ON rankings._driver = drivers.id
    ORDER BY rankings.ranking DESC
    LIMIT 0,20
    ''',
    'all-time-top-peak-progression': '''
    SELECT drivers.driver,
    max_date_rankings.max_rank_date,
    max_date_rankings.max_ranking
    FROM max_date_rankings
    INNER JOIN rankings ON (rankings.ranking = max_date_rankings.max_ranking)
    AND (rankings.rank_date = max_date_rankings.max_rank_date)
    LEFT JOIN drivers ON rankings._driver = drivers.id
    WHERE max_ranking > (
    SELECT MAX(mr.max_ranking) FROM max_date_rankings mr
    WHERE mr.max_rank_date < max_date_rankings.max_rank_date
    )
    ''',
    'top-exit-rankings': '''
    SELECT drivers.driver,
    rankings.ranking,
    rankings.rank_date
    FROM rankings
    INNER JOIN (
    SELECT MAX(rank_date) rank_date, _driver FROM rankings GROUP BY _driver
    ) r ON r.rank_date=rankings.rank_date AND r._driver=rankings._driver
    JOIN drivers ON rankings._driver = drivers.id
    WHERE rankings.rank_date < CURDATE() - INTERVAL 1 YEAR
    ORDER BY rankings.ranking DESC
    LIMIT 0, 20
    ''',
    'top-rankings-by-season': '''
    SELECT tpr.date, tpr.driver, tpr.ranking, tpr.rank_date, tpr.position,
    tar.driver, ROUND(tar.average,2), tar.position,
    c.driver
    FROM top_peak_rankings tpr
    JOIN top_average_rankings tar ON tpr.date = tar.date
    JOIN champions c ON c.year = tpr.date
    ''',
    'top-rookie-end-season-rankings': '''
    SELECT drivers.driver, rankings.rank_date, rankings.ranking
    FROM rankings
    JOIN (
    SELECT MAX(rankings.rank_date) rank_date, rankings._driver
    FROM rankings
    JOIN rookie_seasons ON rookie_seasons.year = YEAR(rankings.rank_date)
    AND rookie_seasons._driver = rankings._driver
    GROUP BY rankings._driver
    ) r ON r.rank_date = rankings.rank_date AND r._driver = rankings._driver
    JOIN drivers ON drivers.id = rankings._driver
    ORDER BY rankings.ranking
    DESC LIMIT 0, 20;
    ''',
    'top-rookie-average-rankings': '''
    SELECT drivers.driver, rookie_seasons.year, AVG(rankings.ranking) ranking
    FROM rankings
    JOIN rookie_seasons ON YEAR(rank_date) = rookie_seasons.year
    AND rookie_seasons._driver = rankings._driver
    JOIN drivers ON drivers.id = rankings._driver
    GROUP BY rankings._driver
    ORDER BY ranking DESC
    LIMIT 0,20;
    ''',
    'season-by-season-inflation': '''
    SELECT date,
    MAX(max_ranking),
    MIN(min_ranking),
    AVG(avg_ranking),
    AVG(avg_ranking)+STDDEV(avg_ranking),
    AVG(avg_ranking)-STDDEV(avg_ranking)
    FROM driver_yearly_rankings
    GROUP BY date
    ORDER BY date ASC;
    '''
    }

    for file, query in raw_queries.iteritems():
        csv = unicodecsv.writer(open('charts/' + file + '.csv', 'w'), lineterminator='\n')
        for result in connection.execute(text(query)):
            csv.writerow(result)

def fetch_decades():
    for decade in range(1950, 2020, 5):
        drivers = []
        for year in range(decade, decade + 5):
            for driver_id in connection.execute(text('''
            (SELECT _driver
            FROM driver_yearly_rankings
            WHERE date = :year
            ORDER BY avg_ranking DESC
            LIMIT 0,3)
            UNION DISTINCT
            (SELECT _driver
            FROM driver_yearly_rankings
            WHERE date = :year
            ORDER BY max_ranking DESC
            LIMIT 0,3)
            '''), year=year):
                drivers.append(driver_id[0])
        rankings = connection.execute(text("SELECT rankings.rank_date, MAX(rankings.ranking), rankings._driver, drivers.* FROM rankings JOIN drivers ON drivers.id = rankings._driver WHERE rank_date >= :date_from AND rank_date <= :date_to AND _driver IN :drivers GROUP BY rankings._driver, rankings.rank_date"), date_from=str(decade)+'-01-01', date_to=str(decade+4)+'-12-31', drivers=drivers)
        csv = unicodecsv.writer(open('charts/' + str(decade) + 's.csv', 'w'))
        tree = lambda: collections.defaultdict(tree)
        table = tree()
        dates = set()
        for row in rankings:
            dates.add(str(row[0]))
            table[row[4]][str(row[0])] = row[1]
        dates = list(dates)
        dates.append('')
        dates = sorted(dates)
        output = []
        output.append(dates)
        for driver, results in table.iteritems():
            row = []
            row.append(driver)
            for date in dates:
                if date:
                    if results.has_key(date):
                        row.append(results[date])
                    else:
                        row.append('')
            output.append(row)
        csv.writerows(output)

def fetch_rolling():
    output = []
    min_date = connection.execute(text('SELECT MIN(date) FROM races')).first()[0].replace(day=1)
    for begin_date in list(rrule.rrule(rrule.MONTHLY, dtstart=min_date, until=date.today())):
        end_date = begin_date + relativedelta.relativedelta(months=6)
        sql = 'SELECT AVG(avg), STDDEV(avg), AVG(dev) FROM (SELECT AVG(ranking) avg, STDDEV(ranking) dev FROM rankings WHERE rank_date BETWEEN :begin_date AND :end_date GROUP BY _driver) avg'
        result = connection.execute(text(sql), begin_date=begin_date, end_date=end_date).first()
        output.append([end_date.strftime('%Y-%m')] + result.values())
    unicodecsv.writer(open('charts/rolling_averages.csv', 'w')).writerows(output)

if len(sys.argv) < 2:
    sys.argv.append('all')

if sys.argv[1] == 'sql':
    fetch_raw()
elif sys.argv[1] == 'decades':
    fetch_decades()
elif sys.argv[1] == 'rolling':
    fetch_rolling()
elif sys.argv[1] == 'all':
    fetch_raw()
    fetch_decades()
    fetch_rolling()
