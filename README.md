# Groww IR Data Fetcher

Automated data collection pipeline for Groww financial metrics with deduplication, CSV storage, and Google Sheets integration.

## Features

✅ **Automatic Data Collection** - Fetches 70 metrics every 5 minutes via GitHub Actions  
✅ **Deduplication** - Metric sheets store only changed values (prevent duplicate rows)  
✅ **Multi-Storage** - CSV (all records) + Google Sheets (All Data + metric-specific sheets)  
✅ **Data Conversion** - Automatic Crores conversion (÷10^7) with proper GMT timestamps  
✅ **Hybrid Execution** - GitHub Actions + local scheduler backup  
✅ **Notifications** - Success/failure alerts via Discord/Slack  

## Project Structure

```
groww-ir-data/
├── .github/
│   └── workflows/
│       └── fetch_groww_ir_data.yml    # GitHub Actions automation (every 5 min)
├── .vscode/
│   └── settings.json                  # VS Code configuration
├── .venv/                             # Python virtual environment
├── Groww/
│   └── IR_Data/
│       ├── fetch_groww_ir_data_with_sheets.py  # Main script (production)
│       ├── scheduler.py                         # Local scheduler backup (every 5 min)
│       ├── .env                                 # Configuration (GitHub token, webhooks)
│       ├── .env.example                         # Configuration template
│       └── google_sheets_creds.json             # Google Sheets credentials
├── requirements.txt                  # Python dependencies
└── README.md                          # This file
```

## Quick Start

### 1. Local Setup

```powershell
# Clone repository
git clone https://github.com/Rachitjainca/groww-ir-data.git
cd groww-ir-data

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` in `Groww/IR_Data/`:
```powershell
cp Groww/IR_Data/.env.example Groww/IR_Data/.env
```

Edit `.env` and fill in:
```env
GITHUB_TOKEN=your_github_token_here
SLACK_WEBHOOK=your_slack_webhook_url (optional)
DISCORD_WEBHOOK=your_discord_webhook_url (optional)
GOOGLE_SHEET_ID=your_sheet_id_here
```

### 3. Set Up Google Sheets (Optional)

Place `google_sheets_creds.json` in `Groww/IR_Data/` (service account credentials)

### 4. Run the Script

**Local execution (single run):**
```powershell
cd Groww/IR_Data
python fetch_groww_ir_data_with_sheets.py
```

**Local scheduler (every 5 minutes):**
```powershell
cd Groww/IR_Data
python scheduler.py
```

## How It Works

### Data Flow

1. **Fetch** → API call to `https://client-pixel.groww.in/api/v1/ir-data/calculate`
2. **Process** → Convert to Crores, format timestamps (GMT)
3. **Deduplicate** → Track previous values in `.previous_metric_values.json`
4. **Store** → 
   - CSV: All 70 records (historical)
   - Google Sheets "All Data": All 70 records (historical)
   - Google Sheets "Metric sheets": Only changed values (deduplication)
5. **Notify** → Send success/failure alerts to Discord/Slack

### Deduplication Logic

```
Run 1: AUM = 31094400 → Saved to metric sheet ✓
Run 2: AUM = 31094400 → Skipped (no change) ✓
Run 3: AUM = 31094405 → Saved to metric sheet (value changed) ✓
```

- **All Data sheet**: Always grows by 70 records per run
- **Metric sheets**: Only grow when values change
- **Tracking file**: `.previous_metric_values.json` (hidden, auto-created)

## GitHub Actions Automation

### Schedule

Runs automatically **every 5 minutes** via GitHub Actions:

```yaml
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes UTC
  workflow_dispatch:       # Manual trigger via UI
```

Activation: Typically 24-48 hours after first push

## Dependencies

- **requests** - HTTP requests
- **pandas** - Data manipulation
- **gspread** - Google Sheets API
- **google-auth** - Google authentication
- **python-dotenv** - Environment variables
- **urllib3** - HTTPS handling
- **schedule** - Local scheduling

See `requirements.txt` for versions.

## File Descriptions

| File | Purpose |
|------|---------|
| `fetch_groww_ir_data_with_sheets.py` | Main production script with deduplication |
| `scheduler.py` | Local backup scheduler (5-min interval) |
| `.env` | Configuration (tokens, webhooks, sheet ID) |
| `.env.example` | Configuration template |
| `google_sheets_creds.json` | Google Sheets service account credentials |
| `.github/workflows/fetch_groww_ir_data.yml` | GitHub Actions automation config |

## Outputs

### CSV Files
- `groww_ir_data.csv` - All records (append-mode)
- Columns: `fetch_time, metric_type, epoch_timestamp, value`

### Google Sheets
- **All Data sheet** - Complete history (all runs, all metrics)
- **Metric sheets** - AUM_Data, CNTU_Data, etc. (deduplicated values only)

### Tracking
- `.previous_metric_values.json` - Previous metric values (for deduplication)

## Troubleshooting

### GitHub Actions not running?
- Wait 24-48 hours for schedule activation (GitHub standard)
- Try one manual trigger: Actions → "Fetch Groww IR Data" → "Run workflow"

### API returning 403 Forbidden?
- Check if Groww API endpoint requires authentication
- Verify IP not rate-limited

### Google Sheets not updating?
- Verify `GOOGLE_SHEETS_CREDENTIALS` is valid JSON
- Check sheet ID is correct and credentials have access

## Notes

- All timestamps are in GMT (DD/MM/YYYY HH:MM:SS format)
- Values converted to Crores (÷10^7) except CNTU metric
- Deduplication applies ONLY to metric sheets (All Data sheet always grows)
- Local scheduler runs every 5 minutes as backup to GitHub Actions

## License

This project is for personal use with Groww API data.
