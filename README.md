# OpenStreetMap Data Munich
In this project the OpenStreetMap Data of Munich (Germany) is explored. It was created for my submission to Udacity's Data Analyst Nanodegree - P3: Wrangling OpenStreetMap Data.

## Project Overview
- **report.md**: main report about data wrangling and analysis
- **problems.md**: details about problems encountered during data wrangling
- **src**: scripts, utility files, OSM sample data

## Source files
In the 'src' folder all the python scripts can be found that were used during data wrangling and analysis. Also, there are utility files and a sample data set of the original OSM file. The full OSM file can be downloaded from https://mapzen.com/data/metro-extracts/metro/munich_germany/.

Following, more details about the source files:

**audit-mapping/**

Includes all utility text files that were created in the wrangling process, either programatically or manually.

**audit_street_names.py**

Script to audit the street names programatically. Uses regular expressions to validate the form. Output is checked manually.

**check_correct.py**

Main functions that check OSM tags and apply corrections, if necessary.

**cleaning.py**

Main script that processes the OSM file, checks and corrects the data and saves everything in CSV files for the database import.

**explore.py**

Interactive shell for exploring the OSM data and find issues. Displays some general information about the tags and then takes tag types to show more details.

**munich_sample.osm**

Small sample from the original Munich OSM file.

**requirements.txt**

Requirements file for installing dependancies with pip.

**schema.py**

Schema file that can be used optionally in 'cleaning.py' to validate data structure.

**util.py**

Utility functions used in several scripts.

## Resources
- OSM sample data was obtained with a script provided by Udacity:
  Data Analyst Nanodegree - P3: Wrangling OpenStreetMap Data > Project > Project Details
- The structure and some of the SQL queries were inspired by the sample project of 'carlward':
  https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
- The 'cleaning.py' script and schema.py are from Udacity and were adopted to the projects needs:
  Data Analyst Nanodegree - P3: Wrangling OpenStreetMap Data > Case Study: OpenStreetMap Data [SQl] > Preparing for Database - SQL
- For the sqlite database the schema of 'swwelch' (linked by Udacity) was used:
  https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f
- As a reference for SQL the official site was used:
  https://www.sqlite.org/lang.html
