# FUNDA SCRAPER 

This is a scraper for the website https://www.funda.nl/.

Currently it scraped for houses to buy. 

Scrapes Funda website and saves the information about houses in a google sheet, based on the filters provided. It also saves the information in a local file, if prefered.
Then reads the google sheet, filters on square meters, neighborhoods and number of bedrooms, and sends a viewing request automatically for the houses that meet the criteria provided.

For now, the viewings preferences and information are set manually.
Preferences include viewing time and days of the week.
Information include email, phone and name.


## How to configure:
- create .env file containing the following variables: SPREADSHEET_ID, RANGE_SHEET
- import your google service account file as `credentials.json` and save them in `\fundascraping\input\`
- fill the `form_data.json` in `\fundascraping\input\form_data.json` with your information to shcedule viewings

## How to run:
Scrape:  `python main.py city nr_pages min_price max_price filename`

Schedule viewings: `python viewing_processor.py m2 neighborhood1,neighborhood2 bedrooms`

Example: 
`python main.py rotterdam 3 200000 500000 test_file`
`python viewing_processor 70 Ommoord,Blijdorp 2`


### Explanation on the input
- city - city for which a house should be searched
- nr_pages - nr of pages to scrape in the website
- min_price - min price for a house
- max_price - max price for a house
- filename - the name of the file containing the results

### Form for viewings (`form_data.json`)
Options available for "Day" (if empty the default is no preference):
- "ma,di,wo,do,vr" (Only workdays)
- "za,zo" (Weekend)
- "ma" (Monday)
- "di" (Tuesday)
- "wo" (Wednesday)
- "do" (Thrusday)
- "vr" (Friday)
- "za" (Saturday)

Options available for "DayPart" (if empty the default is no preference):
- "oc" (In the morning)
- "mi" (In the afternoon)

Options available for "Aanhef" (if empty the default is no preference):
- "Dhr" (Mr)
- "Mevr" (Ms.)
- "Anders" (Other)

Note: Makefile configuration still in progress
