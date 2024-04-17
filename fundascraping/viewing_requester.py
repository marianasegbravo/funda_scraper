import gspread
import os
from dotenv import load_dotenv
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import requests
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

load_dotenv()

class ViewingRequester:
    def __init__(self, m2, neighborhoods, bedrooms):
        self.m2 = m2
        self.neighborhoods = neighborhoods
        self.bedrooms = bedrooms
        self.spreadsheet_id = os.environ['SPREADSHEET_ID']
        self.range_name = os.environ['RANGE_SHEET']
        self.credentials = os.path.join(os.path.dirname(__file__), 'input/credentials.json')
        self.form_data = os.path.join(os.path.dirname(__file__), 'input/form_data.json')

    def read_google_sheet(self):

        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Authenticate using the service account credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials, scope)
        client = gspread.authorize(credentials)

        # Open the Google Sheet by its ID
        sheet = client.open_by_key(self.spreadsheet_id)

        # Select the worksheet by its name
        worksheet = sheet.worksheet(self.range_name)

        # Get all values from the worksheet
        data = worksheet.get_all_values()

        # Convert the data into a DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])

        return df, worksheet

    def filter_data(self, df):
        df["size_m2"] = df["size_m2"].astype(int)
        df["num_of_bedrooms"] = df["num_of_bedrooms"].astype(int)

        # First filter the m2
        if self.m2:
            df_filter_m2 = df[df["size_m2"] >= self.m2]
        else:
            df_filter_m2 = df

        # Second filter the bedrooms
        if self.bedrooms:
            df_filter_bedrooms = df_filter_m2[df_filter_m2["num_of_bedrooms"] >= self.bedrooms]
        else:
            df_filter_bedrooms = df_filter_m2

        # Third filter the neighborhood
        if self.neighborhoods:
            filtered_df = df_filter_bedrooms[df_filter_bedrooms["neighborhood_name"].isin(self.neighborhoods)]
        else:
            filtered_df = df_filter_bedrooms

        return filtered_df

    def viewing_request(self, url):

        session = requests.Session()

        headers = {
                'Referer': url,
                'authority': 'www.google.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'max-age=0',
                'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }

        # Get cookies
        cookies = {
            'bm_sv': '5A3E2F79E9F454008F0FDB3F46505EB7~YAAQjFZhaM/BBaaNAQAA3UIhyxbyX+tOMuHVX9Jxc045KwVgNB2JVMBNQbkMo4l+yFxKYTR9PdB1nV4iQhVvwVOu9UaRDR+uGmB7YIOaWHun5avkhs+x1mItA3iBlwHykNGI8a8j3VhOm4nLbk5Kc5RzyhTXCNFTz72gqngA17ONP1AAnptW56GW87Uf8xAQMl2cNcPDEvGxOLpPY+qbQIDyAypZVEYo9KRgCja6Z+5RWV6vb7+5CVU4A/SYjYY=~1'
        }

        r = session.get(url, headers=headers, cookies=cookies)

        # Parse the HTML content
        soup = BeautifulSoup(r.text, 'html.parser')

        # Extract the value of the __RequestVerificationToken input field
        verification_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

        with open(self.form_data, 'r') as file:
            form_data = json.load(file)
        form_data["__RequestVerificationToken"] = verification_token

        # Submit the form
        response = session.post(url, data=form_data, headers=headers)

        if response.status_code == 200:
            print(f"Form submitted successfully for URL: {url}")
        else:
            print(f"Error: {response.status_code} for URL: {url}")

    def viewing_url(self, df):
        df['url'] = df['url'] + "bezichtiging/"
        return df

    def process_viewing_requests(self):

        # Authenticate with Google Sheets API
        creds = service_account.Credentials.from_service_account_file(
            self.credentials, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=creds)

        df, worksheet = self.read_google_sheet()
        filtered_df = self.filter_data(df)
        filtered_df_with_url = self.viewing_url(filtered_df)
        for index, row in filtered_df_with_url.iterrows():
            success = self.viewing_request(row['url'])
            if success:
                try:
                    cell_range = f"Folha1!U{index + 2}"
                    body = {'values': [['TRUE']]}
                    result = service.spreadsheets().values().update(
                        spreadsheetId=self.spreadsheet_id, range=cell_range,
                        valueInputOption='RAW', body=body).execute()
                    print(f"Updated 'viewing' column for row {index + 2}")
                except Exception as e:
                    print(f"Error updating 'viewing' column for row {index + 2}: {e}")
            return filtered_df_with_url

# # Example usage
# viewing_requester = ViewingRequester(70, ['Oosterflank'], 2)
# viewing_requester.process_viewing_requests()
