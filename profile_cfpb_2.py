"""
profile_cfpb_2.py
Second profile: looks only at closed complaints, EXCLUDING credit reporting.
Shows, for each product: complaint count, monetary relief rate,
narrative rate, and relief rate among complaints that have narratives.
Also counts companies with enough complaints for RQ4.

Run:  python profile_cfpb_2.py   (same folder as the export CSV)
"""
from collections import Counter
import pandas as pd

FILE = "CCDB_Export_September_2023_through_March_2024.csv"   # change to your file name
CHUNK = 500_000
EXCLUDE = "Credit reporting or other personal consumer reports"
CLOSED = ["Closed with monetary relief", "Closed with non-monetary relief",
          "Closed with explanation"]
USE = ["Product", "Company", "Company response to consumer",
       "Consumer complaint narrative"]

total, relief, narr, narr_relief = Counter(), Counter(), Counter(), Counter()
company_n, company_relief = Counter(), Counter()

for c in pd.read_csv(FILE, chunksize=CHUNK, dtype=str, usecols=USE):
    c = c[(c["Product"] != EXCLUDE) & (c["Company response to consumer"].isin(CLOSED))]
    is_relief = c["Company response to consumer"] == "Closed with monetary relief"
    has_text = c["Consumer complaint narrative"].notna()
    total.update(c["Product"])
    relief.update(c.loc[is_relief, "Product"])
    narr.update(c.loc[has_text, "Product"])
    narr_relief.update(c.loc[is_relief & has_text, "Product"])
    company_n.update(c["Company"])
    company_relief.update(c.loc[is_relief, "Company"])

T, R, N, NR = (sum(x.values()) for x in (total, relief, narr, narr_relief))
print(f"CLOSED, NON-CREDIT-REPORTING ROWS: {T:,}")
print(f"  monetary relief: {R:,} ({100*R/T:.2f}%)")
print(f"  with narrative:  {N:,} ({100*N/T:.1f}%)")
print(f"  narrative + relief: {NR:,} ({100*NR/max(N,1):.2f}% of narrative rows)\n")

print(f"{'Product':58s} {'Rows':>8s} {'Relief%':>8s} {'Text%':>7s} {'TextRelief':>10s}")
for p, n in total.most_common():
    print(f"{p[:58]:58s} {n:8,d} {100*relief[p]/n:8.2f} {100*narr[p]/n:7.1f} {narr_relief[p]:10,d}")

for k in (30, 50, 100):
    print(f"\nCompanies with at least {k} closed complaints: "
          f"{sum(1 for v in company_n.values() if v >= k):,}")
