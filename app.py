# import os
# import requests
# import pandas as pd
# from datetime import date, datetime, timedelta
# from flask import Flask, jsonify, send_file

# app = Flask(__name__)

# csv_file_path = "transactions_output.csv"

# def get_token(identifier, password):
#     url = "https://your-api-login-url"
#     payload = {
#         "identifier": identifier,
#         "password": password
#     }
#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         if response.status_code == 200:
#             return response.json().get("token")
#         else:
#             print(f"Failed to login. Status code: {response.status_code}, Response: {response.text}")
#     except Exception as e:
#         print(f"Error while logging in: {e}")
#     return None

# def calculate_time_params():
#     if date:
#         target_date = datetime.strptime(date, "%Y-%m-%d")
#     else:
#         target_date = datetime.now() - timedelta(days=1)

#     from_time = target_date.strftime("%Y%m%d") + "0000"
#     to_time = target_date.strftime("%Y%m%d") + "2359"
#     return from_time, to_time

# def fetch_transactions(token, from_time, to_time):
#     url_template = "https://vdasapi.gtelcds.vn/admin/partner/verify-transactions-mgmt"
#     headers = {"Authorization": f"Bearer {token}"}
#     page_number = 1
#     page_size = 10
#     all_records = []

#     while True:
#         params = {
#             "page_number": page_number,
#             "page_size": page_size,
#             "from_time": from_time,
#             "to_time": to_time
#         }
#         response = requests.get(url_template, headers=headers, params=params)

#         if response.status_code != 200:
#             print(f"Failed to fetch transactions. Status code: {response.status_code}, Response: {response.text}")
#             break

#         data = response.json()
#         records = data.get("data", [])
#         total_pages = data.get("total_page", 1)

#         if not records:
#             break

#         all_records.extend(records)
#         if page_number >= total_pages:
#             break

#         page_number += 1

#     return all_records

# def process_and_save_to_csv(data, output_file):
#     csv_data = []
#     for record in records:
#         csv_data.append({
#             "ID": record["id"],
#             "MSG_ID": record["code"],
#             "CREATE_TIME": record["request_time"],
#             "STATUS_MOS": 1 if record["is_valid_id_card"] else 3
#         })

#     df = pd.DataFrame(csv_data)
#     df.to_csv(csv_file_path, index=False)
#     print(f"CSV saved at {csv_file_path}")

# def test_with_fixed_date(date):
#     identifier = "vcb-0100112437-sandbox" 
#     password = "vcb@#2024"

#     token = get_token(identifier, password)
#     if token:
#         from_time, to_time = calculate_time_params(date)
#         print(f"Fetching data from {from_time} to {to_time}...")
#         records = fetch_transactions(token, from_time, to_time)
#         if records:
#             process_and_save_to_csv(records, csv_file_path)
#         else:
#             print("No data fetched.")
#     else:
#         print("Failed to authenticate.")

# @app.route('/download-csv', methods=['GET'])
# def download_csv():
#     try:
#         # Kiểm tra file tồn tại
#         if not os.path.exists(csv_file_path):
#             return jsonify({"error": "File not found"}), 404

#         # Trả về file CSV
#         return send_file(
#             csv_file_path,  # Đường dẫn đến file CSV
#             mimetype='text/csv',  # MIME type của file
#             as_attachment=True,  # Yêu cầu tải xuống file
#             download_name='transactions.csv'  # Tên file khi tải về
#         )
#     except Exception as e:
#         # Xử lý lỗi khác
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     identifier = "vcb-0100112437-sandbox"  
#     password = "vcb@#2024" 

#     token = get_token(identifier, password)
#     if token:
#         from_time, to_time = calculate_time_params()
#         print(f"Fetching data from {from_time} to {to_time}...")
#         records = fetch_transactions(token, from_time, to_time)
#         if records:
#             process_and_save_to_csv(records, csv_file_path)
#         else:
#             print("No data fetched.")

#     # app.run(debug=True, host='0.0.0.0', port=5000)
#     app.run()


import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_file

app = Flask(__name__)

csv_file_path = "transactions_output.csv"

def get_token(identifier, password):
    url = "https://your-api-login-url"
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
    from_time = target_date.strftime("%Y%m%d") + "0000"
    to_time = target_date.strftime("%Y%m%d") + "2359"
    return from_time, to_time

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

def process_and_save_to_csv(records, output_file):
    csv_data = [
        {
            "ID": record["id"],
            "MSG_ID": record["code"],
            "CREATE_TIME": record["request_time"],
            "STATUS_MOS": 1 if record["is_valid_id_card"] else 3
        }
        for record in records
    ]

    df = pd.DataFrame(csv_data)
    df.to_csv(output_file, index=False)
    print(f"CSV saved at {output_file}")

def initialize_data():
    """Fetch and save transaction data to CSV."""
    identifier = "vcb-0100112437-sandbox"
    password = "vcb@#2024"

    token = get_token(identifier, password)
    if token:
        from_time, to_time = calculate_time_params()
        print(f"Fetching data from {from_time} to {to_time}...")
        records = fetch_transactions(token, from_time, to_time)
        if records:
            process_and_save_to_csv(records, csv_file_path)
        else:
            print("No data fetched.")
    else:
        print("Failed to authenticate.")

@app.route('/download-csv', methods=['GET'])
def download_csv():
    try:
        if not os.path.exists(csv_file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(
            csv_file_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='transactions.csv'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
