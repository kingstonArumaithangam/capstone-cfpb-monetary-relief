# Data

## Source
- Publisher: Consumer Financial Protection Bureau (CFPB)
- Collection: Consumer Complaint Database – Narratives Archive
- Archive page: https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/
- Export file: CCDB_Export_5_September_2023_through_March_2024.csv
- Complaint period: 1 September 2023 to 31 March 2024
- Downloaded on: October 3, 2026
- Field definitions: https://cfpb.github.io/api/ccdb/fields.html

## Raw file (not stored here)
- Rows: 945,532
- Columns: 16
- Size: about 618.3 MB uncompressed

## Scoped file (stored here)
- File: cfpb_scoped.csv.gz
- Rows: 163,699
- Size: 38.1 MB (gzip)
- Rules applied:
  1. Excluded "Credit reporting or other personal consumer reports"
  2. Kept only closed complaints (closed with monetary relief,
     closed with non-monetary relief, closed with explanation)

## Reproduce
1. Download the export file from the archive page.
2. Place it in this folder.
3. Run: python scripts/capstone_findings.py
4. Compare the output with outputs/findings_report.txt



## Citation
Consumer Financial Protection Bureau. (2026). [exact archive title] [Data set].
https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/
