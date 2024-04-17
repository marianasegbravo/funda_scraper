import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
class FundaKoopScraping:

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def __init__(self, city, nr_pages, min_price, max_price, filename):
        self.city = city # string
        self.nr_pages = nr_pages # int
        self.min_price = min_price # int
        self.max_price = max_price # int
        self.filename = filename # string
        self.urls = None
        self.selector = None
        self.data = None
        self.df = None
        self.credentials = os.path.join(os.path.dirname(__file__), 'input/credentials.json')

    def retrieving_urls(self):
        print("-------------- Getting houses URLs --------------")
        main_url = f'https://www.funda.nl/en/zoeken/koop?selected_area=%5B%22{self.city}%22%5D'
        page = 1
        self.urls = []

        while page <= self.nr_pages:
            url = f'{main_url}&search_result={page}'
            r = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            script_tag = soup.find_all("script", {"type": "application/ld+json"})[0]
            json_data = json.loads(script_tag.contents[0])

            for item in json_data["itemListElement"]:
                url = item["url"].replace("koop", "en/koop")
                self.urls.append(url)

            page += 1

        print("-------------- URLs retrieved --------------")
        return self.urls

    def clean_css(self, soup, selector):
        result = soup.select(selector)
        if len(result) > 0:
            result = result[0].text.replace('\n', '').replace('\r', '').strip()
        else:
            result = "na"
        return result

    def scrape_info(self):
        print("-------------- Scraping funda --------------")
        self.data = []
        for url in self.urls:
            r = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            info = {
                "house_id": str(re.findall(r"-(\d+)-", url)[0]),
                "price": self.clean_css(soup, ".object-header__price"),
                "address": self.clean_css(soup, ".object-header__title"),
                "description": self.clean_css(soup, ".object-description-body"),
                "zip_code": self.clean_css(soup, ".object-header__subtitle"),
                "size": self.clean_css(soup, ".fd-m-right-xl--bp-m .fd-text--nowrap"),
                "year": self.clean_css(soup, ".fd-align-items-center~ .fd-align-items-center .fd-m-right-xs"),
                "url": url,
                "living_area": self.clean_css(soup, ".object-kenmerken-list:nth-child(8) .fd-align-items-center:nth-child(2) span"),
                "num_of_rooms": self.clean_css(soup, ".object-kenmerken-list:nth-child(11) .fd-align-items-center:nth-child(2)"),
                "num_of_bedrooms": self.clean_css(soup, ".object-kenmerken-list:nth-child(11) .fd-align-items-center:nth-child(2)"),
                "num_of_bathrooms": self.clean_css(soup, ".object-kenmerken-list:nth-child(11) .fd-align-items-center:nth-child(4)"),
                "energy_label": self.clean_css(soup, ".energielabel"),
                "insulation": self.clean_css(soup, ".object-kenmerken-list:nth-child(14) .fd-align-items-center:nth-child(4)"),
                "ownership": self.clean_css(soup, ".object-kenmerken-list:nth-child(17) .fd-align-items-center:nth-child(4)"),
                "parking": self.clean_css(soup, ".object-kenmerken-list:nth-child(24)"),
                "status": self.clean_css(soup, ".object-kenmerken-list:nth-child(2) .fd-align-items-center:nth-child(8)"),
                "exteriors": self.clean_css(soup, ".object-kenmerken-list:nth-child(19)"),
                "neighborhood_name": self.clean_css(soup, ".fd-display-inline--bp-m")
            }
            self.data.append(info)

        self.df = pd.DataFrame(self.data)

        print("-------------- Scraping funda complete --------------")
        return self.df

    def clean_int(self, text):
        text = str(text)
        try:
            return int(re.findall(r'\d+', text)[0])
        except (ValueError, IndexError):
            return 0

    def clean_prices(self, text):
        text = str(text)
        try:
            return int(text.replace('k.k','').replace(',','').replace('.','').replace('€','').strip())
        except (ValueError, IndexError):
            return 0

    def clean_rooms(self, text):
        try:
            return int(str(text)[0])
        except (ValueError, IndexError):
            return 0

    def clean_bedrooms(self, text):
        text = str(text)
        try:
            return int(re.findall(r'\d+', text)[1])
        except (ValueError, IndexError) as e:
            print(f"IndexError occurred: {e}")
            return 0

    def clean_bathroom(self, text):
        text = str(text)
        try:
            bathrooms = [int(item) for item in re.findall(r'\d+', text)]
            return sum(bathrooms)
        except (ValueError, IndexError):
            return 0

    def clean_information(self, text):
        """
        used for columns like parking and exterior where more than one output might exist
        :param text:
        :return:
        """
        result = ''
        for char in text:
            if char.isupper():
                result += ' ' + char
            else:
                result += char
        try:
            return result
        except (ValueError, IndexError):
            return 0

    def clean_data(self):
        print("-------------- Cleaning columns information and type loading -------------- ")
        self.df["price"] = self.df["price"].apply(self.clean_prices)
        self.df["zip_code"] = self.df["zip_code"].apply(self.clean_int)
        self.df["living_area"] = self.df["living_area"].apply(self.clean_int)
        self.df["size"] = self.df["size"].apply(self.clean_int)
        self.df["num_of_rooms"] = self.df["num_of_rooms"].apply(self.clean_rooms)
        self.df["num_of_bedrooms"] = self.df["num_of_bedrooms"].apply(self.clean_bedrooms)
        self.df["num_of_bathrooms"] = self.df["num_of_bathrooms"].apply(self.clean_bathroom)
        self.df["parking"] = self.df["parking"].apply(self.clean_information)
        self.df["exteriors"] = self.df["exteriors"].apply(self.clean_information)
        print("-------------- Cleaning columns complete --------------")
        return self.df

    def clean_table(self):
        print("-------------- Re-organizing table --------------")
        df_rename = self.df.rename(columns={'price': 'price(€)', 'size': 'size_m2', 'living_area': 'living_area_m2'})
        df_re_order = df_rename.reindex(columns=['house_id','status', 'address', 'zip_code', 'neighborhood_name', 'year', 'price(€)', 'size_m2',
                                                 'living_area_m2', 'num_of_rooms', 'num_of_bedrooms', 'num_of_bathrooms',
                                                 'energy_label', 'url', 'description', 'ownership', 'insulation', 'parking',
                                                 'exteriors'])
        df_re_order["created_at"] = str(datetime.now())
        df_re_order["viewing"] = "FALSE"
        filtered_df = df_re_order[(df_re_order['price(€)'] >= self.min_price) & (df_re_order['price(€)'] <= self.max_price)]
        self.df = filtered_df
        # self.df = filtered_df.set_index('house_id')
        print("-------------- Table complete --------------")
        return self.df

    def save_to_csv(self):
        print("-------------- Saving file --------------")
        # Check if the output folder exists, if not, create it
        if not os.path.exists("output"):
            os.makedirs("output")
        # Save the CSV file inside the output folder
        self.df.to_csv(f"output/{self.filename}.csv", index=False, sep=';')
        print(f"{self.filename} file saved! ✅")

    def update_google_sheet(self):
        # Authenticate with Google Sheets API
        creds = service_account.Credentials.from_service_account_file(
            self.credentials, scopes=['https://www.googleapis.com/auth/spreadsheets'])
        service = build('sheets', 'v4', credentials=creds)

        # Define the spreadsheet ID and range
        spreadsheet_id = os.environ['SPREADSHEET_ID']
        range_name = os.environ['RANGE_SHEET']

        # Fetch existing data from the Google Sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        existing_data = result.get('values', [])

        # Extract existing house IDs from the existing data
        existing_house_ids = set(row[0] for row in existing_data)

        # Filter the DataFrame to get only rows where house-id doesn't already exist
        new_rows = self.df[~self.df["house_id"].isin(existing_house_ids)]

        if not new_rows.empty:
            # Prepare the new data to be appended to the Google Sheet
            data = new_rows.values.tolist()

            if not existing_data:
                # If no existing cells, include column names along with the new data
                data = [self.df.columns.tolist()] + data

            # Write data to Google Sheet
            body = {
                'values': data
            }
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption='RAW', body=body).execute()

            # Calculate the number of cells updated based on the number of rows in the new data
            num_rows_updated = len(data) - 1 if not existing_data else len(data)  # Exclude header row if it was added

            print('{0} cells updated.'.format(num_rows_updated))
        else:
            print("No new data to append.")

