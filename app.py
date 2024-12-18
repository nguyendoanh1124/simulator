import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import random

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

    total_records = len(data)

    # Ngẫu nhiên quyết định giữ nguyên hoặc áp dụng ±5% số lượng bản ghi
    keep_original_count = random.choice([True, False])

    if not keep_original_count:
        # Randomize number of records (+-5%)
        variation = int(total_records * 0.05)  # 5% của tổng số bản ghi
        random_count = total_records + random.randint(-variation, variation)  # Số lượng bản ghi sau khi ngẫu nhiên
        random_count = max(1, min(random_count, total_records))  # Đảm bảo số lượng không vượt quá giới hạn

        # Chọn ngẫu nhiên các bản ghi
        sampled_data = random.sample(data, random_count)
    else:
        # Giữ nguyên số lượng bản ghi
        sampled_data = data

    csv_data = []
    for record in sampled_data:
        # Convert CREATE_TIME to desired format
        raw_time = record["request_time"]
        formatted_time = datetime.strptime(raw_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        
        csv_data.append({
            "ID": record["id"],
            "MSG_ID": record["code"],
            "CREATE_TIME": formatted_time,
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

def calculate_seconds_to_midnight():
    now = datetime.now()
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_to_midnight = (midnight - now).total_seconds()
    return seconds_to_midnight

if __name__ == "__main__":
    # Run the first job immediately
    print("Running the first job...")
    run_daily_job()

    while True:
        seconds_to_sleep = calculate_seconds_to_midnight()
        print(f"Sleeping for {seconds_to_sleep:.0f} seconds until midnight...")
        time.sleep(seconds_to_sleep)

        print("Running the daily job at midnight...")
        run_daily_job()
