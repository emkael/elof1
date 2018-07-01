DROP VIEW IF EXISTS champions;
CREATE VIEW champions AS
	SELECT championship.year, drivers.driver, championship.points
	FROM championship
	JOIN drivers
		ON drivers.id = championship._driver
	WHERE championship.position = 1;

DROP VIEW IF EXISTS driver_seasons_count;

CREATE VIEW driver_seasons_count AS
	SELECT YEAR(rank_date) year, _driver, COUNT(rank_date) count
	FROM rankings GROUP BY _driver, YEAR(rank_date);

DROP VIEW IF EXISTS driver_yearly_rankings;

CREATE VIEW driver_yearly_rankings AS
	SELECT MAX(rankings.ranking) max_ranking, AVG(rankings.ranking) avg_ranking, MIN(rankings.ranking) min_ranking,
           YEAR(rankings.rank_date) date, COUNT(rankings.id) count, MIN(championship.position) position, rankings._driver
	FROM rankings
	LEFT JOIN championship ON rankings._driver = championship._driver AND YEAR(rankings.rank_date) = championship.year
	GROUP BY YEAR(rankings.rank_date), rankings._driver;

DROP VIEW IF EXISTS max_date_rankings;

CREATE VIEW max_date_rankings AS
	SELECT MAX(ranking) max_ranking, rank_date max_rank_date
	FROM rankings GROUP BY rank_date;

DROP VIEW IF EXISTS rookie_seasons;

CREATE VIEW rookie_seasons AS
	SELECT MIN(year) year, _driver
	FROM driver_seasons_count
	WHERE count > 6
	GROUP BY _driver;

DROP VIEW IF EXISTS `top_yearly_rankings`;

CREATE VIEW top_yearly_rankings AS
	SELECT MAX(max_ranking) peak, MAX(avg_ranking) average, date
	FROM driver_yearly_rankings
	WHERE count > 10
	GROUP BY date;

DROP VIEW IF EXISTS top_average_rankings;

CREATE VIEW top_average_rankings AS
	SELECT top_yearly_rankings.date, drivers.driver, top_yearly_rankings.average, driver_yearly_rankings.position
	FROM top_yearly_rankings
		JOIN driver_yearly_rankings ON driver_yearly_rankings.avg_ranking = top_yearly_rankings.average
			AND driver_yearly_rankings.date = top_yearly_rankings.date
		JOIN drivers ON driver_yearly_rankings._driver = drivers.id
	WHERE driver_yearly_rankings.count > 10;

DROP VIEW IF EXISTS top_peak_rankings;

CREATE VIEW top_peak_rankings AS
	SELECT top_yearly_rankings.date, drivers.driver, rankings.ranking, rankings.rank_date, driver_yearly_rankings.position
	FROM rankings
		JOIN top_yearly_rankings ON YEAR(rankings.rank_date) = top_yearly_rankings.date AND rankings.ranking = top_yearly_rankings.peak
		JOIN drivers ON rankings._driver = drivers.id
		JOIN driver_yearly_rankings ON rankings._driver = driver_yearly_rankings._driver AND top_yearly_rankings.date = driver_yearly_rankings.date;
