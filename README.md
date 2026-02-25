# Groww IR Data Fetcher

Automated hourly data fetcher for Groww's Investor Relations metrics, with dual output to CSV and Google Sheets.

## Features

✨ **Automated Hourly Fetch** - GitHub Actions runs every hour (0 * * * * UTC)  
📊 **Dual Output** - CSV backup + Google Sheets primary storage  
📈 **Metric Sheets** - Separate sheets for each metric type (AUM, CNTU, MF assets, etc.)  
🔐 **Secure** - Credentials stored in GitHub Secrets, not in code  
📝 **Append-only** - Historical data accumulates without overwriting  

## Quick Setup (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/Rachitjainca/groww-ir-data.git
cd groww-ir-data
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. Google Sheets Setup
- Create a Google Cloud project and service account
- Download credentials JSON file
- Share your Google Sheet with the service account email
- Save credentials as `Groww/IR_Data/google_sheets_creds.json`
- Create `.env` file: `GOOGLE_SHEET_ID=your_sheet_id`

### 4. Test Locally
```bash
cd Groww/IR_Data
python fetch_groww_ir_data_with_sheets.py
```

### 5. Deploy to GitHub
```bash
# Add GitHub Secrets (Settings > Secrets):
# - GOOGLE_SHEET_ID: Your sheet ID
# - GOOGLE_SHEETS_CREDENTIALS: Full JSON file contents

git add .
git commit -m "Initial setup"
git push origin main
```

## Data Structure

**CSV Output:** `Groww/IR_Data/groww_ir_data.csv`
```
fetch_time, metric_type, epoch_timestamp, timestamp_readable, value
2026-02-25 19:10:37, CNTU, 1740502237000, 25/02/2026 19:10:37, 12345
```

**Google Sheets:**
- **All Data** - Complete record of all fetches (70 records/hour)
- **CNTU_Data** - Customer count metrics
- **AUM_Data** - Assets under management
- **mf_assets_Data** - Mutual fund assets
- **mf_sip_inflows_Data** - SIP inflows
- **equity_adto_Data** - Equity ADTO
- **stocks_adto_Data** - Stocks ADTO
- **stocks_assets_Data** - Stocks assets

## API Reference

**Endpoint:** `https://client-pixel.groww.in/api/v1/ir-data/calculate`  
**Method:** GET  
**Returns:** 70 metrics across 7 types, 10 values each  
**Rate:** Not rate-limited, safe for hourly calls  

## Documentation

- [Google Sheets Setup Guide](Groww/IR_Data/GOOGLE_SHEETS_SETUP.md) - Detailed step-by-step instructions
- [Quick Setup](Groww/IR_Data/QUICK_SETUP_SHEETS.md) - Fast reference for GitHub Actions

## Scripts

- `fetch_groww_ir_data_with_sheets.py` - Main script (CSV + Google Sheets)
- `fetch_groww_ir_data.py` - CSV-only backup version

## Files & Privacy

- `google_sheets_creds.json` - **Never commit!** (in .gitignore)
- `.env` - **Never commit!** (in .gitignore)
- CSV & JSONL data files - Tracked in git for data history

## Automation Status

✅ Hourly schedule: `0 * * * * *` (every hour at :00 UTC)  
✅ GitHub Actions: Configured in `.github/workflows/fetch_groww_ir_data.yml`  
✅ Automatic commits: CSV changes pushed hourly  
✅ Artifact backup: 30-day retention in Actions  

## Troubleshooting

**"ModuleNotFoundError: No module named 'gspread'"**
```bash
pip install -r requirements.txt
```

**"Google Sheet is empty"**
- Verify service account email is shared with Edit access on sheet
- Check GitHub Secrets are set correctly
- Run workflow manually and check logs

**"SSL Certificate Error"**
- This is handled automatically in the script with `verify=False`

## License

MIT

## Status

🟢 **Production Ready** - Tested with 70 records/hour sync to Google Sheets
