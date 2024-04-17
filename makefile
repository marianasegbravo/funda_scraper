
# Define environment variables file
ENV_FILE = .env

## Define the path to the credentials JSON file
#CREDENTIALS_JSON = 'credentials.json'

# Load environment variables
include $(ENV_FILE)
export $(shell sed 's/=.*//' $(ENV_FILE))

.PHONY: help install scrape clean docs viewings

install:  virtualenv $(VENV_NAME) && $(VENV_NAME)/bin/activate && pip install -r requirements.txt

scrape:
	python main.py $(city) $(nr_pages) $(min_price) $(max_price) $(filename)
# example usage: make scrape city=rotterdam nr_pages=3 min_price=250000 max_price=500000 filename=test

viewings:
	python viewing_processor.py $(m2) $(neighborhoods) $(bedrooms)
# example usage: make viewing_processor m2=70 neighborhoods=neighborhood1, neighborhood2 bedrooms=2
