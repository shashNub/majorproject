import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

def scrape_all_homepage_tables(url="https://www.freejobalert.com/latest-notifications/"):
    print(f"📄 Scraping ALL tables from: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    all_rows = []
    all_headers_set = set()

    for idx, table in enumerate(tables):
        print(f"➡️ Scraping Table {idx + 1}")
        header_row = table.find("tr")
        if not header_row:
            continue

        headers = [th.get_text(strip=True).replace('Bank Name', 'Name') for th in header_row.find_all("th")]
        all_headers_set.update(headers)

        for tr in table.find_all("tr")[1:]:  # Skip the header row
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cols) == len(headers):
                row_dict = dict(zip(headers, cols))
                all_rows.append(row_dict)

    return list(all_headers_set), all_rows

def clean_data(rows, headers):
    # Convert list of dictionaries into a DataFrame for easier manipulation
    df = pd.DataFrame(rows)

    # Remove leading and trailing spaces from all columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Handle missing or NaN values (e.g., replace with 'N/A' or drop rows/columns)
    df = df.fillna("N/A")

    # Remove duplicates
    df = df.drop_duplicates()

    # Return cleaned data as list of dictionaries again
    return df.to_dict(orient='records'), df.columns.tolist()

def save_to_csv(headers, rows, filename="freejobalert_latest_notifications.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"\n✅ DONE: Cleaned and saved {len(rows)} total rows to {filename}.")

def scrape_and_save(filename="freejobalert_latest_notifications.csv"):
    headers, rows = scrape_all_homepage_tables()
    cleaned_rows, cleaned_headers = clean_data(rows, headers)
    save_to_csv(cleaned_headers, cleaned_rows, filename)
    return cleaned_rows

if __name__ == "__main__":
    scrape_and_save()
