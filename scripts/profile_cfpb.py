"""
profile_cfpb.py
Quick profile of the CFPB Consumer Complaint Database.
Gives the numbers needed for the synopsis: size, date range,
missing values, relief rate, digital payment share, narratives.

1. Download "complaints.csv.zip" from
   https://www.consumerfinance.gov/data-research/consumer-complaints/
2. Unzip it. Put complaints.csv in the same folder as this script.
3. Run:  python profile_cfpb.py
4. Copy the printed output back to the chat.

Reads the file in chunks, so it works on a normal laptop.
"""
from collections import Counter
import pandas as pd

FILE = "complaints.csv"
CHUNK = 500_000

# Print the real column names first (CFPB sometimes renames columns)
cols = pd.read_csv(FILE, nrows=0).columns.tolist()
print("COLUMNS:", cols, "\n")

DATE, PROD, NARR = "Date received", "Product", "Consumer complaint narrative"
RESP, TIMELY, COMP = "Company response to consumer", "Timely response?", "Company"
CHANNEL, DUP_ID = "Submitted via", "Complaint ID"

rows = 0
missing = Counter()
products, responses, timely, channels = Counter(), Counter(), Counter(), Counter()
companies = Counter()
years = Counter()
narr_count = 0
min_date, max_date = None, None
ids = set()
dup_ids = 0

for chunk in pd.read_csv(FILE, chunksize=CHUNK, dtype=str, low_memory=False):
    rows += len(chunk)
    missing.update(chunk.isna().sum().to_dict())
    products.update(chunk[PROD].fillna("MISSING"))
    responses.update(chunk[RESP].fillna("MISSING"))
    timely.update(chunk[TIMELY].fillna("MISSING"))
    channels.update(chunk[CHANNEL].fillna("MISSING"))
    companies.update(chunk[COMP].fillna("MISSING"))
    if NARR in chunk.columns:
        narr_count += chunk[NARR].notna().sum()
    d = pd.to_datetime(chunk[DATE], errors="coerce")
    years.update(d.dt.year.dropna().astype(int))
    lo, hi = d.min(), d.max()
    min_date = lo if min_date is None or lo < min_date else min_date
    max_date = hi if max_date is None or hi > max_date else max_date
    for cid in chunk[DUP_ID].dropna():
        if cid in ids:
            dup_ids += 1
        else:
            ids.add(cid)

print(f"TOTAL ROWS: {rows:,}")
print(f"DATE RANGE: {min_date.date()} to {max_date.date()}")
print(f"DUPLICATE COMPLAINT IDs: {dup_ids:,}")
if NARR in cols:
    print(f"ROWS WITH NARRATIVE: {narr_count:,} ({100*narr_count/rows:.1f}%)")
else:
    print("ROWS WITH NARRATIVE: column not present in this file")
print(f"UNIQUE COMPANIES: {len(companies):,}\n")

print("MISSING VALUES (% of rows):")
for c in cols:
    print(f"  {c}: {100*missing[c]/rows:.1f}%")

print("\nPRODUCTS (all, with counts):")
for p, n in products.most_common():
    print(f"  {p}: {n:,} ({100*n/rows:.1f}%)")

print("\nCOMPANY RESPONSE:")
for r, n in responses.most_common():
    print(f"  {r}: {n:,} ({100*n/rows:.1f}%)")

print("\nTIMELY RESPONSE:")
for t, n in timely.most_common():
    print(f"  {t}: {n:,} ({100*n/rows:.1f}%)")

print("\nSUBMITTED VIA:")
for s, n in channels.most_common():
    print(f"  {s}: {n:,}")

print("\nCOMPLAINTS PER YEAR:")
for y in sorted(years):
    print(f"  {y}: {years[y]:,}")

print("\nTOP 10 COMPANIES:")
for c, n in companies.most_common(10):
    print(f"  {c}: {n:,} ({100*n/rows:.1f}%)")
