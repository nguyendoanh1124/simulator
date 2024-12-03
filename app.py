import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

CSV_DIRECTORY = "data"
os.makedirs(CSV_DIRECTORY, exist_ok=True)

def get_token(identifier, password):
    url = "https://vdasgateway.gtelcds.vn/login"
    payload = {"identifier": identifier, "password": password}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get("token")
        else:
            print(f"Failed to login. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error while logging in: {e}")
    return None

def calculate_time_params():
    target_date = datetime.now() - timedelta(days=1)
    from_time = target_date.strftime("%Y%m%d") + "0001"
    to_time = target_date.strftime("%Y%m%d") + "2359"
    date_str = target_date.strftime("%Y-%m-%d")
    return from_time, to_time, date_str

def fetch_transactions(token, from_time, to_time):
    url_template = "https://vdasapi.gtelcds.vn/admin/partner/verify-transactions-mgmt"
    headers = {"Authorization": f"Bearer {token}"}
    page_number = 1
    page_size = 10
    all_records = []

    while True:
        params = {
            "page_number": page_number,
            "page_size": page_size,
            "from_time": from_time,
            "to_time": to_time
        }
        response = requests.get(url_template, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch transactions. Status code: {response.status_code}, Response: {response.text}")
            break

        data = response.json()
        records = data.get("data", [])
        total_pages = data.get("total_page", 1)

        if not records:
            break

        all_records.extend(records)
        if page_number >= total_pages:
            break
        page_number += 1
    return all_records

def process_and_save_to_csv(data, date_str):
    if not data:
        print(f"No transaction data available for {date_str}. Skipping CSV generation.")
        return

    csv_data = []
    for record in data:
        csv_data.append({
            "ID": record["id"],
            "MSG_ID": record["code"],
            "CREATE_TIME": record["request_time"],
            "STATUS_MOS": 1 if record["is_valid_id_card"] else 3
        })

    output_file = os.path.join(CSV_DIRECTORY, f"transaction_{date_str}.csv")
    
    df = pd.DataFrame(csv_data, columns=["ID", "MSG_ID", "CREATE_TIME", "STATUS_MOS"])
    df.to_csv(output_file, index=False)
    
    print(f"CSV saved at {output_file} (rows: {len(csv_data)})")

def run_daily_job():
    try:
        identifier = "vcb-0100112437-sandbox"
        password = "vcb@#2024"

        token = get_token(identifier, password)
        if not token:
            print("Authentication failed. Exiting.")
            return

        from_time, to_time, date_str = calculate_time_params()
        print(f"Fetching data for {date_str}...")

        records = fetch_transactions(token, from_time, to_time)
        process_and_save_to_csv(records, date_str)

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    print("Running the first job...")
    run_daily_job()

    while True:
        print("Sleeping for 1 day...")
        time.sleep(86400) 
        print("Running the daily job...")
        run_daily_job()
