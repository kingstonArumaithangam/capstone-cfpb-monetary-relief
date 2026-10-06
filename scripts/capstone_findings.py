"""
capstone_findings.py
QM 640 Capstone - Kingston
One script that reproduces EVERY number used in the proposal and synopsis.

What it does (in order):
  Part A  Raw data profile      (size, dates, duplicates, text, products)
  Part B  Scope and cleaning    (exclude credit reporting, keep closed)
  Part C  Findings by product   (relief rate, text rate)
  Part D  Predictors for RQ1    (counts dummy columns from the real data)
  Part E  Sample size per RQ    (all formulas calculated, not typed in)
  Part F  Hypotheses table      (H0 and H1 for RQ1 to RQ4)

Output: printed on screen AND saved to findings_report.txt (for GitHub).

Setup:
  pip install pandas scipy statsmodels
  Put the CFPB archive export CSV in the same folder.
  Run:  python capstone_findings.py
"""
import math
from collections import Counter

import pandas as pd
from scipy.stats import norm
from statsmodels.stats.power import GofChisquarePower

# ----------------------------------------------------------------- settings
FILE = "CCDB_Export_September_2023_through_March_2024.csv"  # your file name
CHUNK = 500_000
ALPHA, POWER = 0.05, 0.80
EXCLUDE = "Credit reporting or other personal consumer reports"
CLOSED = ["Closed with monetary relief", "Closed with non-monetary relief",
          "Closed with explanation"]
RELIEF = "Closed with monetary relief"
RQ2_PRODUCTS = ["Money transfer, virtual currency, or money service",
                "Prepaid card", "Checking or savings account", "Credit card"]
TOP_ISSUES = 15          # RQ1: keep top 15 issues, group the rest as "Other"
MIN_COMPANY = 30         # RQ4: companies need at least 30 closed complaints
EPV = 10                 # RQ1: events per variable (Peduzzi et al., 1996)
RQ2_W = 0.10             # RQ2: small effect size (Cohen, 1988)
RQ3_RECALL, RQ3_BASE, RQ3_TEST = 0.70, 0.60, 0.20
RQ4_R = 0.30             # RQ4: medium correlation (Cohen, 1988)

# US Census regions (states not listed, e.g. territories, become "Other")
REGION = {}
for region, states in {
    "Northeast": "CT ME MA NH RI VT NJ NY PA",
    "Midwest": "IL IN MI OH WI IA KS MN MO NE ND SD",
    "South": "DE DC FL GA MD NC SC VA WV AL KY MS TN AR LA OK TX",
    "West": "AZ CO ID MT NV NM UT WY AK CA HI OR WA",
}.items():
    for s in states.split():
        REGION[s] = region

# ----------------------------------------------------------------- helpers
lines = []


def out(text=""):
    print(text)
    lines.append(str(text))


def pct(a, b):
    return 100 * a / b if b else 0.0


# ----------------------------------------------------------------- read data
USE = ["Date received", "Product", "Issue", "Company", "State", "Tags",
       "Submitted via", "Company response to consumer",
       "Consumer complaint narrative", "Complaint ID"]

raw_rows, raw_text, dup_ids = 0, 0, 0
raw_products, raw_companies, raw_response = Counter(), Counter(), Counter()
seen, min_d, max_d = set(), None, None
keep = []

for c in pd.read_csv(FILE, chunksize=CHUNK, dtype=str, usecols=USE):
    raw_rows += len(c)
    raw_text += c["Consumer complaint narrative"].notna().sum()
    raw_products.update(c["Product"])
    raw_companies.update(c["Company"])
    raw_response.update(c["Company response to consumer"].fillna("MISSING"))
    d = pd.to_datetime(c["Date received"], errors="coerce")
    min_d = d.min() if min_d is None else min(min_d, d.min())
    max_d = d.max() if max_d is None else max(max_d, d.max())
    for cid in c["Complaint ID"]:
        dup_ids += cid in seen
        seen.add(cid)
    c = c[(c["Product"] != EXCLUDE) & c["Company response to consumer"].isin(CLOSED)]
    keep.append(c.drop(columns=["Date received", "Complaint ID"]))

df = pd.concat(keep, ignore_index=True)
df["relief"] = (df["Company response to consumer"] == RELIEF).astype(int)
df["has_text"] = df["Consumer complaint narrative"].notna().astype(int)

# ----------------------------------------------------------------- Part A
out("=" * 70)
out("PART A  RAW DATA PROFILE")
out("=" * 70)
out(f"Source file:            {FILE}")
out(f"Total complaints:       {raw_rows:,}")
out(f"Date range:             {min_d.date()} to {max_d.date()}")
out(f"Duplicate IDs:          {dup_ids:,}")
out(f"With narrative text:    {raw_text:,} ({pct(raw_text, raw_rows):.1f}%)")
cr = raw_products[EXCLUDE]
out(f"Credit reporting:       {cr:,} ({pct(cr, raw_rows):.1f}%)")
top3 = raw_companies.most_common(3)
out(f"Top 3 companies share:  {pct(sum(n for _, n in top3), raw_rows):.1f}%  "
    f"({', '.join(name for name, _ in top3)})")
out("Company response (all rows):")
for k, v in raw_response.most_common():
    out(f"   {k}: {v:,} ({pct(v, raw_rows):.1f}%)")

# ----------------------------------------------------------------- Part B
N, R, T = len(df), df["relief"].sum(), df["has_text"].sum()
TR = df.loc[df["has_text"] == 1, "relief"].sum()
p = R / N
p_text = TR / T
out()
out("=" * 70)
out("PART B  SCOPE AFTER CLEANING")
out("=" * 70)
out("Rule 1: exclude credit reporting (dominant product, 3 bureaus).")
out("Rule 2: keep only closed complaints (outcome must be known).")
out(f"Rows kept:              {N:,}")
out(f"Monetary relief:        {R:,} ({100*p:.2f}%)")
out(f"With narrative:         {T:,} ({pct(T, N):.1f}%)")
out(f"Relief among narrative: {TR:,} ({100*p_text:.2f}%)")

# ----------------------------------------------------------------- Part C
out()
out("=" * 70)
out("PART C  FINDINGS BY PRODUCT")
out("=" * 70)
g = df.groupby("Product").agg(rows=("relief", "size"), relief=("relief", "mean"),
                              text=("has_text", "mean")).sort_values("rows", ascending=False)
out(f"{'Product':55s} {'Rows':>8s} {'Relief%':>8s} {'Text%':>7s}")
for prod, r in g.iterrows():
    out(f"{prod[:55]:55s} {int(r.rows):8,d} {100*r.relief:8.2f} {100*r.text:7.1f}")
lo, hi = g["relief"].idxmin(), g["relief"].idxmax()
out(f"Lowest relief:  {lo} ({100*g.loc[lo,'relief']:.2f}%)")
out(f"Highest relief: {hi} ({100*g.loc[hi,'relief']:.2f}%)")
out(f"Gap:            {g.loc[hi,'relief']/g.loc[lo,'relief']:.0f} times")

# ----------------------------------------------------------------- Part D
top_issues = df["Issue"].value_counts().index[:TOP_ISSUES]
issue_g = df["Issue"].where(df["Issue"].isin(top_issues), "Other")
region = df["State"].map(REGION).fillna("Other")
levels = {
    "Product": df["Product"].nunique(),
    f"Issue (top {TOP_ISSUES} + Other)": issue_g.nunique(),
    "Region (Census + Other)": region.nunique(),
    "Submitted via": df["Submitted via"].nunique(),
    "Tags (incl. none)": df["Tags"].fillna("None").nunique(),
}
k = sum(v - 1 for v in levels.values())
out()
out("=" * 70)
out("PART D  RQ1 PREDICTOR COLUMNS (one category per feature is the baseline)")
out("=" * 70)
for name, v in levels.items():
    out(f"   {name:30s} {v:3d} categories -> {v-1:3d} columns")
out(f"   k (total predictor columns) = {k}")

# ----------------------------------------------------------------- Part E
z = norm.ppf(1 - ALPHA / 2) + norm.ppf(POWER)       # about 2.80
n1 = math.ceil(EPV * k / p)

rq2 = df[df["Product"].isin(RQ2_PRODUCTS)]
df2 = (len(RQ2_PRODUCTS) - 1) * (2 - 1)
n2 = math.ceil(GofChisquarePower().solve_power(effect_size=RQ2_W, n_bins=df2 + 1,
                                                alpha=ALPHA, power=POWER))

pos3 = math.ceil((z * 0.5 / (RQ3_RECALL - RQ3_BASE)) ** 2)
n3 = math.ceil(pos3 / p_text / RQ3_TEST)

counts = df.groupby("Company")["relief"].agg(["size", "mean"])
companies = (counts["size"] >= MIN_COMPANY).sum()
n4 = math.ceil((z / (0.5 * math.log((1 + RQ4_R) / (1 - RQ4_R)))) ** 2 + 3)

table = [
    ("RQ1", "Events per variable (logistic regression)",
     f"EPV={EPV}, k={k}, p={p:.4f}", f"{EPV} x {k} / {p:.4f}", n1, N),
    ("RQ2", "Power of test (chi-square)",
     f"alpha={ALPHA}, power={POWER}, w={RQ2_W}, df={df2}", "statsmodels solve_power", n2, len(rq2)),
    ("RQ3", "Power of test (recall, proportion)",
     f"recall {RQ3_RECALL} vs {RQ3_BASE}, prevalence={p_text:.4f}, test={RQ3_TEST}",
     f"({z:.2f} x 0.5 / {RQ3_RECALL-RQ3_BASE:.2f})^2 = {pos3} positives; / {p_text:.4f} / {RQ3_TEST}",
     n3, T),
    ("RQ4", "Power of test (Pearson, Fisher z)",
     f"alpha={ALPHA}, power={POWER}, r={RQ4_R}", "((z)/(0.5 ln((1+r)/(1-r))))^2 + 3", n4, companies),
]
out()
out("=" * 70)
out("PART E  SAMPLE SIZE BY RESEARCH QUESTION")
out("=" * 70)
for rq, method, params, calc, need, have in table:
    out(f"{rq}  {method}")
    out(f"     Parameters:  {params}")
    out(f"     Calculation: {calc}")
    out(f"     Minimum N:   {need:,}    Available: {have:,}    "
        f"{'OK' if have >= need else 'NOT ENOUGH'}")
biggest = max(table, key=lambda r: r[4])
out(f"Largest minimum: {biggest[0]} = {biggest[4]:,}")

# ----------------------------------------------------------------- Part F
hyp = [
    ("RQ1", "No complaint feature is associated with monetary relief (all beta = 0).",
     "At least one complaint feature is associated with monetary relief."),
    ("RQ2", "The monetary relief rate is the same across the four payment products.",
     "The monetary relief rate differs across the four payment products."),
    ("RQ3", "The text-based model's recall for monetary relief is not higher than the "
            "structured-feature baseline (recall <= 0.60).",
     "The text-based model's recall for monetary relief is higher than the "
     "structured-feature baseline (recall > 0.60)."),
    ("RQ4", "There is no correlation between company complaint volume and relief rate (rho = 0).",
     "There is a correlation between company complaint volume and relief rate (rho != 0)."),
]
out()
out("=" * 70)
out("PART F  HYPOTHESES")
out("=" * 70)
for rq, h0, h1 in hyp:
    out(f"{rq}  H0: {h0}")
    out(f"     H1: {h1}")

with open("findings_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\nSaved: findings_report.txt")
