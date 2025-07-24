import argparse
import os
import re
import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

GOOGLE_FINANCE_QUOTE_URL = "https://www.google.com/finance/quote/{}"


def fetch_prices(ticker: str):
    """Return current and open price for ticker from Google Finance."""
    url = GOOGLE_FINANCE_QUOTE_URL.format(ticker)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    price_el = soup.find("div", {"class": "YMlKec fxKbKc"})
    if not price_el:
        raise ValueError(f"Current price not found for {ticker}")
    current_price = float(price_el.text.replace(",", ""))

    # try to find the day's open value from the html
    open_val = None
    open_label = soup.find(string="Open")
    if open_label:
        open_el = open_label.find_parent("div")
        if open_el:
            val_el = open_el.find_next("div")
            if val_el and val_el.text:
                try:
                    open_val = float(val_el.text.replace(",", ""))
                except ValueError:
                    pass
    if open_val is None:
        # fallback regex search
        m = re.search(r'"open":\{"raw":([\d.]+)', html)
        if m:
            open_val = float(m.group(1))

    return current_price, open_val


def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.environ['EMAIL_FROM']
    msg['To'] = os.environ['EMAIL_TO']

    with smtplib.SMTP_SSL(
        os.environ['SMTP_SERVER'], int(os.environ['SMTP_PORT'])
    ) as server:
        server.login(os.environ['SMTP_USERNAME'], os.environ['SMTP_PASSWORD'])
        server.sendmail(msg['From'], [msg['To']], msg.as_string())


def check_ticker(ticker: str, threshold: float):
    current_price, open_price = fetch_prices(ticker)
    if open_price is None:
        return
    drop = (open_price - current_price) / open_price * 100
    if drop >= threshold:
        subject = f"{ticker} dropped {drop:.2f}%"
        body = (
            f"Ticker {ticker} price is {current_price}, opened at {open_price}.\n"
            f"Drop: {drop:.2f}% (threshold {threshold}%)"
        )
        send_email(subject, body)


def main():
    parser = argparse.ArgumentParser(description="Check Google Finance for price drops")
    parser.add_argument("--tickers", required=True, help="Comma separated tickers, e.g. AAPL:NASDAQ,GOOG:NASDAQ")
    parser.add_argument("--threshold", required=True, type=float, help="Drop percentage threshold")
    args = parser.parse_args()

    tickers = [t.strip() for t in args.tickers.split(',') if t.strip()]
    for ticker in tickers:
        try:
            check_ticker(ticker, args.threshold)
        except Exception as exc:
            print(f"Error processing {ticker}: {exc}")


if __name__ == "__main__":
    main()
