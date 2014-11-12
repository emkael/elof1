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
SELECT YEAR(rank_date),
       MAX(ranking),
       MIN(ranking),
       AVG(ranking),
       AVG(ranking)+STDDEV(ranking),
       AVG(ranking)-STDDEV(ranking)
FROM rankings
GROUP BY YEAR(rank_date)
ORDER BY YEAR(rank_date) ASC;
```
