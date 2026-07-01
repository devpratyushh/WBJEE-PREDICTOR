import requests
import pandas as pd
from io import StringIO
import os

def fetch_and_save_data():
    urls = {
        "2021": "https://admissions.nic.in/wbjeeb/applicant/report/orcrreport.aspx?enc=Nm7QwHILXclJQSv2YVS+7t5O5EVrvqMhdk/bbq9ioFjahMV3TyfdCGo7ms/IlfkE",
        "2022": "https://admissions.nic.in/wbjeeb/applicant/report/orcrreport.aspx?enc=Nm7QwHILXclJQSv2YVS+7hcjwg9gJLL3dN9nSB9R2fAEJ/7sG2MvnUlvdh4rG3CN",
        "2023": "https://admissions.nic.in/wbjeeb/Applicant/report/orcrreport.aspx?enc=b6w3EPyuw0C4FADZ4v1XmYUz0XFq314fzLjkE3wbM2xr/DbsjpvUS9LBCKXjSeSL",
        "2024": "https://admissions.nic.in/wbjeeb/Applicant/report/orcrreport.aspx?enc=Nm7QwHILXclJQSv2YVS+7l8OpFY/O746kfneOXEneV50mv1B/txHsSKB11hFlsvw",
        "2025": "https://admissions.nic.in/wbjeeb/Applicant/report/orcrreport.aspx?enc=Nm7QwHILXclJQSv2YVS+7ud0s9OnRxxLItScoKR31F4qbKNJ7YB3loiJ7DTFho11"
    }

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.6",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Brave\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "cross-site",
        "sec-fetch-user": "?1",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }

    cookies = {
        "ASP.NET_SessionId": "5kx3r2oh0bydkddcoucjnjaa"
    }
    
    os.makedirs("data", exist_ok=True)

    print("Starting batch data fetch...")
    
    for year, url in urls.items():
        output_csv = f"data/{year}.csv"
        
        if os.path.exists(output_csv):
            print(f"[{year}] data already exists at {output_csv}, skipping download.")
            continue
            
        print(f"\nFetching data for {year}...")
        response = requests.get(url, headers=headers, cookies=cookies)
        
        if response.status_code == 200:
            print(f"[{year}] Successfully fetched page. Extracting tables...")
            try:
                html_content = StringIO(response.text)
                tables = pd.read_html(html_content)
                
                if not tables:
                    print(f"[{year}] No tables found on the page.")
                    continue
                    
                main_table = max(tables, key=len)
                
                # Use utf-8 encoding to prevent Windows cp1252 errors when saving
                main_table.to_csv(output_csv, index=False, encoding="utf-8")
                
                print(f"[{year}] Data successfully saved! ({len(main_table)} rows)")
                
            except Exception as e:
                print(f"[{year}] Error extracting tables: {e}")
        else:
            print(f"[{year}] Request failed with status code: {response.status_code}")
            
    print("\nBatch fetch complete! Streamlit will automatically pick up the new files.")

if __name__ == "__main__":
    fetch_and_save_data()
