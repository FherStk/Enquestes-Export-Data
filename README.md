# Enquestes-Export-Data

This repository contains 2 different tools to generate reports from different sources.

## report_from_postgresql.py
This tool generates a report from a PostgreSQL database.

### How to run
1. Installing the Psycopg2 library is required: `pip install psycopg2-binary`
2. Make sure you have set up your correct PostgreSQL connection parameters at the "conn" variable.
3. Run: `report_from_postgresql.py`

---

##  report_from_csv.py
This tool generates a report from a Google Forms' CSV results file. The form needs to contain a list of 1 to 10 scale-based questions and 1 last open-text question.


### How to run
1. Place your Google Forms' CSV exported file in the root folder.
2. Run: `python report.py your-source-file.csv your-report-title`(e.g. `python report.py dummy_poll.csv "Dummy poll report"`).

---

## Extra contents
Added the following files as test examples:

### report_from_csv.py related:
- report_from_postgresql_demo.html: Report generated through report_from_csv.py.

###  report_from_csv.py related:
- csv_dummy_poll.csv: Dummy data to generate a report with report_from_csv.py.
- csv_dummy_poll.html: Dummy report generated through report_from_csv.py after the "csv_dummy_poll.csv" file using "Dummy poll report" as title.
