Challenges and issues with the rating process
=============================================

Two main obstacles had to be overcome to achieve satisfactory quality of the analysis and the entire project.

One of them was purely technical, the other - theoretical/methodological. This documents presents them very briefly.

Gathering and unifying data
---------------------------

The project obviously involved dealing with lots of race and qualifying results (well, basically, with *all* of it).

The usual process of compiling results into project database consisted of several steps:

1. scraping data from various public web sources
2. converting data to consistent format (i.e. CSV)
3. semi-manual compilation of data in the CSV to importable format
4. importing CSV data to project database
5. normalization of imported data

### Scraping the data

At first, I tried to use Wikipedia as an initial source for race results. Since any source with uniform tabular would do just fine, it seemed like a good idea at the time. Unfortunately, wikipedia is far from uniform. Throughout 1000+ wikipedia pages for both championship and non-championship races, not only the format of the results table varies, but the number of tables (separate qualifying table vs. "grid" column), or the placement and headings of the tables, as well.

Plus, Wikipedia is far from being complete in terms of non-championship races results. And since that meant I would need a separate data source anyway, fighting with Wikipedia scrape automation didn't seem worth it (despite the presence of a proper API for fetching revisions of wiki pages).

The next source, this time with consitently formatted tables, was [A Second A Lap blog](http://second-a-lap.blogspot.com/) - which showcases one ray each day. Main advantage of the source: lightweight native Blogspot API for fetching article contents. Main (and critical) flaw: the series is in the mid-60s as of now so the data would not be complete for a long time. Also, the tables lacked entry numbers, a nice flavour in the data.

Fortunately, that's were [Ergast Developer API](http://ergast.com/mrd/db) came in handy. The SQL database image provided an achievable baseline for testing the algorithm (on championship race results and the qualifying data included in the dump). As a side-effect, after running some checks on the Ergast-imported data, some inconsistencies were detected and reported to Ergast maintainers.

The initial source for non-championship races was then chosen: [The Formula One Archives](http://www.silhouet.com/motorsport/archive/f1/title.html). That meant dealing with plain-text data and lots of manual aligning of the data to form columns. Surprisingly, CSV-formatted data manipulation in any office software works very well so this wasn't as hard as it seemed.

Yet still, there was a need for qualifying/prequalifying data not included in Ergast DB. So the ultimate source (without which compiling wouldn't be possible in relatively short time) was the magnificent [Chicane F1 website](http://chicanef1.com/). Despite some minor errors in the data (most likely - propagation of print errors from original sources, small things like wrong digits in timing which then lead to incorrect qualifying speeds by which I had to sort my data to discard grid penalties), the website data turned out bullet-proof (comprehensive, consistent, covering at least everything covered in other sources) and dataset was completed.

### Scraped data conversion

The conversion process for the sources which I managed to automate happened on the fly. The helper script for both scraping and HTML->CSV conversion is available in the dumps/ directory of project tree.

The directory includes:

 * scrapers for chicanef1 and second-a-lap single result pages
 * scrapers which extract all possible qualifying and non-championship result page URLs from chicane
 * utility which fetches URLs and converts the tables to CSV files and compiles multiple CSV files to single file, producing the list of compiled files as a side-effect

**I urge you to proceed with highest level of attention when trying to scrape the websites on your own using these tools.**
They involve lots of excess requests (since it was easier to fetch everything that moves and filter out the weeds afterwards) and may generate substantial bandwidth on the source websites if used without common sense. And the last thing I'd want is to cause trouble to the amazing people who put these data for public access in the first place.

### Compiling the data

The most time-consuming and boring part of the whole process. Extending the CSV data to accomodate algorithm's ranking criteria. Spread sheet manual labor with lots of filtering, sanity checks, conditional formulas, more filtering, more formula etc.

Nothing useful in terms of source-code or data not included in the resulting database came up from this stage, apart from a sense of satisfaction and drastic appreciation of spreadsheet software.

### Importing the data

That's where the result database structure kicks in. For clarity, I'll show you the schema first:

    +---------+           +------------+
    |  races  |           | race_types |
    +---------+ 0..*    1 +------------+
    | + date  |-----------| + code     |
    | + race  |     _type +------------+
    +---------+
       1 | _race
         |
    0..* |
    +-----------------+                  +-----------+              +--------------+
    |     entries     |                  |  drivers  |              |   rankings   |
    +-----------------+                  +-----------+ 1       0..* +--------------+
    | + result        | 0..*        0..* | + driver  |--------------| + ranking    |
    | + car_no        |------------------| + country | _driver      | + rank_date  |
    | + result_group  | _entry   _driver +-----------+              +--------------+
    +-----------------+ (driver_entries)

Since `race_types` table is a pre-filled dictionary and values in `rankings` are only calculated by the main rating application, dataset import operates on `races`, `entries` and `drivers`.

The `races` table is pretty much straight-forward, so CSV-formatted file can easily be imported into the table (e.g. with the help of any proper web-based RDBMS administration tool).

The aim of main import procedure was to populate the `drivers`, `driver_entries` and `entries` tables, with - if possible - shared drives support.

That pushed some constraints on the amount of information and format of the imported CSV file. Very rudimentary import script (import-csv.py) assumes CSV file with either of the following line formats:

 * 6 columns: race ID, text description of entry result, car number, driver country, driver name, result group for Elo algorithm outcome
 * 2 columns: driver country, driver name

Detecting first row format created a new entry for race, the second one - appended another driver to a shared drive for the last processed entry. On top of that, the `drivers` table was being filled with every driver name not yet present in the database.

### Data normalization

Usually after running import script, the main concern was the normalization of driver names present in the database. Since lookup and identification of drivers during the import took only their into account, there were lots of duplicates - drivers racing under nicknames, drivers with multiple names they'd figured under or drivers with various spelling variant of their names.

After manual normalization of such values, the dataset was ready for processing (usually - resetting the ranking DB to the date of first newly imported session and running the rating onwards).

Preventing ranking inflation/deflation
--------------------------------------

Applying Elo rating algorithm to a selected sample of players and not to a wider spectrum of skill among competitors has several flaws.

It's highly unlikely that the distribution of skill among drivers who already reached the top class of motorsports is compatible with normal distribution or logistic distribution, which makes it rather inconvenient for purposes of Elo rating.

The evolution of ranking values over time is sensitive to various effects:

 * drivers entering the sport aren't "rookies" with negligible skill (in the classic algorithm: until some number of ranked games)
 * drivers with lower skill tend to leave the sport sooner than drivers with higher skill
 * the conditions which influence outcomes of duels between drivers change rapidly due to technical development and/or team changes - so the likelyhood of yet lower rated driver defeating higher rated driver is sometimes unpredictable (and long streaks of lower ranked drivers defeating higher ranked drivers are not uncommon, which leads to constant "leap-frogging" in the rankings and rapid rating changes)

In classical Elo model (i.e. players entering the rankings with fairly low ranking, with constant disparity factor of the game) this leads to ranking inflation over time. This can be managed to some extent by a few simple adjustement of Elo parameters:

 * the entry ranking for new players (which can be changed in application configuration and has been set at a fairly high level of 2000 points)
 * the threshold ranking values for decreasing rating changes coming from duels (by default the thresholds are set so that newcomers already fall into the middle interval and very quickly fall into the highest interval, while it's still possible for them to fall into to lower interval of higher rating swings)
 * the disparity value of the field (lower value tends to stop already dominating drivers from gaining even more advantage while higher value is better when the field is less predictive, e.g. at the beginning of the season)

The aforementioned adjustements made thigns slightly better, but the model was still unstable, as it was very easy to overcorrect - which, in turn, led to rating deflation and underappreciation of drivers as time went by.

From the beginning I hoped to avoid switching to some more complex algorithms, like Glicko, and to stay as closely to core Elo rating as possible. Yet some changes were still necessary.

As I've already mentioned in the write-up of pairing and ranking method (see: doc/results.txt), the field disparity can be adjusted dynamically. The more the ratings change over recent time, the lower the disparity (so that initial shift of power among the grid pushes the drivers closer the top but prevents their dominanve to escalate until the ratings are stabilized again).

The cut-off had to be more subtle than linear decrease of disparity, so the following formula was used:

`disparity` = `base_disparity` * 0.5 * (2.5 + `base_rating_change` / (`rating_change` - 2 * `base_rating_change`))) [if `rating_change` <= `base_rating_change`]

`disparity` = 0.75 * `base_disparity` [if `rating_change` >= `base_rating_change`], where:

 * `base_disparity` and `base_rating_change` are application parameters
 * `rating_change` is average amplitude of driver rating for previous 3 months (max(rating) - min(rating) over 3 months for every driver, averaged)

The equation may look scary, but it's just a concave segment of hyperbolic function, spanning from `base_disparity` in 0 to 75% of `base_disparity` in `base_rating_change` and staying constant for higher values of rating change. The adjustement can be turned off in application configuration.

Now, it has to be said that if you have a predetermined bias or prejudice for (or against) certain drivers or decades, it's fairly easy to tweak the algorithm so that it yields results that satisfy you. For the results I'm showing, I tried my best to keep overall ranking conditions over the entire field constant over time. It's debatable if that's not defeating the entire point of the simulation - one of the main reasons for using Elo-like rating was to separate absolute driver achievements (yes, "achievements", not "skill", since comparisons among the entire field do not factor out technical level of cars driven by competitors) from the general "quality" of the grid they're fielded against. But as the average rating is comparable over decades, the variation is not - so some conclusions on overall quality of certain grids can be drawn.

For full disclosure purposes: simple tweaks to field disparity either underline the achievements of Fangio era (with rapid inflation of rating in the early years - the fact that the sport got dominated that much not long after the beginning doesn't help) or Vettel's achievements (with inflation kicking in around Schumacher era). It's interesting to see, though, that no matter which way the absolute ratings are skewed, last decade of the sport shows signs of "standing on the shoulders of giants": Alonso, by defeating Schumacher in 2005-06, gets higher ratings, which then are being surpassed by Vettel and, sometimes, Hamilton at the moment. Basically - beating highly rated drivers in a space of 1-2 seasons elevates a driver even higher.
