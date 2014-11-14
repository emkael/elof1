Overview
========

This application allows to apply Elo-like rankings to Formula One races.

Requirements
============

 * python 2.x (developed and tested on 2.7.8)
 * SQLAlchemy
 * PySQLite (optional)
 * MySQL connector for python (optional)
 * dateutil

Import scripts use some additional libraries, such as:

 * BeautifulSoup4
 * lxml
 * urllib, urllib2, urlparse

You can use the application with either SQLite database or MySQL database (in that case you, well, need a MySQL database).

Installation
============

1. Fetch this repository
2. Configure your database (see: Configuration:Database)
3. Fill the database with result data
4. All done!

Usage
=====
```
usage: elo.py [-h] [--date DATE] [--limit LIMIT] [-v] [--force] [COMMAND]

positional arguments:
  COMMAND        Action to execute against the database:
                 print - prints the rankings for all drivers ranked in 12 months,
                 reset - resets the rankings,
                 rate - calculates the rankings
                 init - init clean database for the application
                 Default value is 'print'.

optional arguments:
  -h, --help     show this help message and exit
  --date DATE    Date for which the action should be executed.
                 Print ratings for DATE,
                 reset ratings all the way down to DATE
                 or rank the races all the way up to DATE.
  --limit LIMIT  Ranking list (display) cut-off point.
  -v             Display verbose info on rating progress to STDERR.
  --force, -f    Force database initialization (for "init" command).
```

Configuration
=============

Application configuration consists of two JSON-formatted files: elo.json and db.json.

Database
--------

`db.json` holds database configuration. Two example files (for both MySQL and SQLite) are provided. If you want a quick-start solution, just rename the `db.json.SQLITE-EXAMPLE` to `db.json`.

The first time you run the application against a fresh database, you have to initialize the structure, by running:

    ./elo.py init

At any time, you can do a hard reset on the existing database, by running init with `--force` parameter. This truncates all the data, including race results data from the database, and recreates the structure.

Results data are provided in elo.db pre-filled SQLite database or in sql/results.sql, in plain SQL format.

Elo parameters
--------------

`elo.json` contains algorithm parameter for Elo ratings:

 * initial driver ranking
 * algorithm disparity options
 * algorithm importance for distinct race types (championship/non-championship, qualifying/race)
 * algorithm importance thresholds

Remember that any change to parameters should lead to ranking reset (`./elo.py reset; ./elo.py rate`) if you want consistent rating criteria throughout the entires time span of results database.

More information
================

More elaborate write-up of the methodology and general approach to the problem can be found in the doc/ directory of source code repository, which contains:

 * races.md: explanation of race selection for the results database
 * results.md: summary of the scoring method
 * sources.md: summary of sources used for result data
 * challenges.md: two most dificult aspects of the project, described in detail
 * sql.md: useful or interesting queries to be run against the database (may only be applicable to the MySQL database)

Author
======

If you want to contact me about the application, you can drop me a private message on Reddit: /u/emkael (although I know it's not exactly rocket science to work out other means of communication, from the GitHub account alone). I'll do my best to help.

License
=======

lol, idk.

Do: use it, share it, mix it, modify it, analyse it - just leave some attribution.

Don't: sell it?
