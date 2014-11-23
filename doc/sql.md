Useful queries for application database:
=======================================

 * overall top rating progression

```
CREATE OR REPLACE VIEW max_date_rankings AS
       SELECT MAX(ranking) max_ranking,
              rank_date max_rank_date
       FROM rankings
       GROUP BY rank_date;
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
);
```

 * overall top peak ratings

```
SELECT drivers.driver,
       rankings.ranking,
       rankings.rank_date
FROM rankings
INNER JOIN (
      SELECT MAX(ranking) ranking, _driver FROM rankings
      GROUP BY _driver
) r ON r.ranking=rankings.ranking AND r._driver=rankings._driver
JOIN drivers ON rankings._driver = drivers.id
GROUP BY rankings._driver
ORDER BY rankings.ranking DESC;
```

 * highest exit ratings

```
SELECT drivers.driver,
       rankings.ranking,
       rankings.rank_date
FROM rankings
INNER JOIN (
      SELECT MAX(rank_date) rank_date, _driver FROM rankings GROUP BY _driver
) r ON r.rank_date=rankings.rank_date AND r._driver=rankings._driver
JOIN drivers ON rankings._driver = drivers.id
WHERE rankings.rank_date < CURDATE() - INTERVAL 1 YEAR
ORDER BY rankings.ranking DESC;
```

 * year-by-year rating inflation

```
CREATE OR REPLACE VIEW driver_yearly_rankings AS
    SELECT MAX(rankings.ranking) max_ranking,
           AVG(rankings.ranking) avg_ranking,
           MIN(rankings.ranking) min_ranking,
           YEAR(rankings.rank_date) date, COUNT(rankings.id) count,
           championship.position, rankings._driver
    FROM rankings
    LEFT OUTER JOIN championship ON rankings._driver = championship._driver
                                 AND YEAR(rankings.rank_date) = championship.year
    GROUP BY YEAR(rankings.rank_date), rankings._driver;

SELECT date,
       MAX(max_ranking),
       MIN(min_ranking),
       AVG(avg_ranking),
       AVG(avg_ranking)+STDDEV(avg_ranking),
       AVG(avg_ranking)-STDDEV(avg_ranking)
FROM driver_yearly_rankings
GROUP BY date
ORDER BY date ASC;
```


    CREATE OR REPLACE VIEW top_yearly_rankings AS
        SELECT MAX(max_ranking) peak, MAX(avg_ranking) average, date
        FROM driver_yearly_rankings
        WHERE count > 10
        GROUP BY date;

    CREATE OR REPLACE VIEW top_peak_rankings AS
        SELECT top_yearly_rankings.date, drivers.driver, rankings.ranking, rankings.rank_date,
               driver_yearly_rankings.position
        FROM rankings
        JOIN top_yearly_rankings ON YEAR(rankings.rank_date) = top_yearly_rankings.date
                                 AND rankings.ranking = top_yearly_rankings.peak
        JOIN drivers ON rankings._driver = drivers.id
        JOIN driver_yearly_rankings ON rankings._driver = driver_yearly_rankings._driver
                                    AND top_yearly_rankings.date = driver_yearly_rankings.date
        GROUP BY top_yearly_rankings.date;

    CREATE OR REPLACE VIEW top_average_rankings AS
        SELECT top_yearly_rankings.date, drivers.driver,
               top_yearly_rankings.average, driver_yearly_rankings.position
        FROM top_yearly_rankings
        JOIN driver_yearly_rankings ON driver_yearly_rankings.avg_ranking = top_yearly_rankings.average
                                    AND driver_yearly_rankings.date = top_yearly_rankings.date
        JOIN drivers ON driver_yearly_rankings._driver = drivers.id
        WHERE driver_yearly_rankings.count > 10;

    CREATE OR REPLACE VIEW champions AS
        SELECT championship.year, drivers.driver, championship.points
        FROM championship
        JOIN drivers ON drivers.id = championship._driver
        WHERE position = 1;

    CREATE OR REPLACE VIEW driver_seasons_count AS
        SELECT YEAR(rank_date) year, _driver, COUNT(rank_date) count
        FROM rankings
        GROUP BY _driver, YEAR(rank_date);

    CREATE OR REPLACE VIEW rookie_seasons AS
        SELECT MIN(year) year, _driver
        FROM driver_seasons_count
        WHERE count > 6
        GROUP BY _driver;

    SELECT *
    FROM races
    JOIN (
        SELECT MIN(date) min_date
        FROM races
        WHERE _type = 3
        GROUP BY YEAR(date)
    ) m ON m.min_date = races.date
    WHERE _type = 3;

    SELECT *
    FROM races
    JOIN (
        SELECT MAX(date) max_date
        FROM races
        WHERE _type = 4
        GROUP BY YEAR(date)
    ) m ON m.max_date = races.date
    WHERE _type = 4;

