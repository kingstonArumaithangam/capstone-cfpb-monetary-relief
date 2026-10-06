# Predicting Monetary Relief in Consumer Financial Complaints

QM 640 Data Analytics Capstone – Walsh College
Student: Kingston A
Mentor: Keya Choudhury Ganguli

## What this project does
This project studies consumer complaints sent to the CFPB.
It looks at which complaints end with monetary relief
(the customer gets money back).
It also checks if the complaint text helps to predict this.

## Research questions
1. Which complaint features are linked to monetary relief?
2. Do relief rates differ across four payment products?
3. Does complaint text improve prediction over structured data?
4. Is company complaint volume linked to the relief rate?

## Data
- Source: CFPB Consumer Complaint Database – Narratives Archive
- File: CCDB_Export_5_September_2023_through_March_2024.csv
- Period: September 2023 to March 2024
- Raw data: 945,532 complaints
- Scoped data: 163,699 closed complaints (in the data folder)
- More details: see data/README.md

## Folder structure

capstone-cfpb-monetary-relief/
├── README.md
├── data/
│ ├── README.md
│ └── cfpb_scoped.csv.gz
├── scripts/
│ ├── profile_cfpb.py
│ ├── profile_cfpb_2.py
│ └── capstone_findings.py



## How to run
1. Install Python 3.9 or higher.
2. Install the libraries:
   pip install pandas scipy statsmodels
3. Download the raw CSV file (link in data/README.md).
4. Put the CSV file in the same folder as the script.
5. Run:
   python scripts/capstone_findings.py
6. The output is saved as findings_report.txt.

## What each script does
| Script | Purpose |
|---|---|
| profile_cfpb.py | First look at the raw data: size, missing values, products |
| profile_cfpb_2.py | Relief rate and text rate by product, after filtering |
| capstone_findings.py | All key numbers, sample sizes and hypotheses in one run |


## Status
Synopsis stage. Models for RQ1 to RQ4 will be added later.
