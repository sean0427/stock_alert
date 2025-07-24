# stock_alert

This repository contains a simple script and GitHub Actions workflow to check
stock prices from Google Finance and send an email alert when a price drops more
than a given percentage.

## Configuration

1. Define the following secrets in your repository settings:
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `EMAIL_TO`
   - `EMAIL_FROM`

2. Optionally set default tickers and threshold as repository environment
   variables `TICKERS` and `THRESHOLD`.

## Running locally

```
uv pip install -r requirements.txt
python check_google_finance.py --tickers AAPL:NASDAQ,GOOG:NASDAQ --threshold 5
```

## GitHub Actions

The workflow in `.github/workflows/stock_alert.yml` runs every 30 minutes during
US market hours (14:30–21:00 UTC) and can also be triggered manually with
`workflow_dispatch`.
