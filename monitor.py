import requests
import os
import dotenv
import json
import time
import logging

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

URL = "https://www.aa.com/offers/bff/products"

# The PAYLOAD will be created dynamically for each confirmation code
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://www.aa.com',
    'referer': 'https://www.aa.com/reservation/view/find-your-trip',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
}

class Monitor:
    def __init__(self):
        confirmation_codes_env = os.getenv('CONFIRMATION_CODE', '')
        self.confirmation_codes = [code.strip() for code in confirmation_codes_env.split(',') if code.strip()]
        
        if not self.confirmation_codes:
            logging.error("No confirmation codes found in environment variables!")
            raise ValueError("No confirmation codes found!")
            
        # Dictionary to store price and data for each confirmation code
        self.prices = {}
        self.data_dict = {}
        
        # Initialize prices for all confirmation codes
        for code in self.confirmation_codes:
            price, data = self.get_price_for_code(code)
            self.prices[code] = price
            self.data_dict[code] = data
            
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        self.delay = 60  # seconds

        if not self.discord_webhook:
            logging.error("No Discord Webhook URL found in environment variables!")
            raise ValueError("No Discord Webhook URL found!")

    def get_price_for_code(self, confirmation_code):
        """Fetch the upgrade price from AA's API for a specific confirmation code."""
        payload = {
            "metadata": {
                "clientId": "AACOM",
                "journeyPath": "INSTANT_UPSELL",
                "locale": "en_US",
                "cartId": ""
            },
            "recordLocator": confirmation_code,
            "currency": "USD"
        }
        
        try:
            logging.info(f"Checking price for confirmation code: {confirmation_code}")
            response = requests.post(URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()

            teasers = data.get('teaser', [])
            if not teasers:
                logging.error(f"No teasers found in response for code {confirmation_code}.")
                return None, None
                
            for teaser in teasers:
                content = teaser.get('content', {})
                if not content:
                    logging.error(f"No content found in teaser for code {confirmation_code}.")
                    return None, None
                    
                if content.get('cabinType') == 'FIRST':
                    price = content.get('offerPrice')
                    logging.info(f"Price to upgrade to First for {confirmation_code}: ${price}")
                    return price, content
                    
            return None, None
        except requests.RequestException as e:
            logging.error(f"Failed to fetch price for {confirmation_code}: {e}")
            return None, None

    def check_price(self):
        """Continuously check for price changes across all confirmation codes and send notifications."""
        try:
            while True:
                for code in self.confirmation_codes:
                    new_price, new_data = self.get_price_for_code(code)
                    
                    # Skip if price couldn't be fetched
                    if new_price is None:
                        continue
                        
                    old_price = self.prices.get(code)
                    
                    if new_price != old_price:
                        logging.info(f"Price changed for {code} from {old_price} to {new_price}")
                        self.prices[code] = new_price
                        self.data_dict[code] = new_data
                        self.send_discord_embed(code, old_price, new_price)
                    else:
                        logging.info(f"Price has not changed for {code}.")

                time.sleep(self.delay)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user.")

    def send_discord_embed(self, confirmation_code, old_price, new_price, title="✈️ Flight Upgrade Alert", color=0x5865F2):
        """Send a Discord embed notification when the price changes."""
        if not self.discord_webhook:
            logging.warning("No Discord webhook URL found.")
            return
        
        data = self.data_dict.get(confirmation_code, {})
        price_change = "decreased" if new_price < old_price else "increased"
        description = f"Price has {price_change} for flight {confirmation_code}!"
        
        embed = {
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": color,
                    "fields": [
                        {"name": "Confirmation Code", "value": confirmation_code, "inline": False},
                        {"name": "Old Price", "value": f"${old_price}" if old_price else "N/A", "inline": True},
                        {"name": "New Price", "value": f"${new_price}", "inline": True},
                        {"name": "Currency", "value": "USD", "inline": True},
                        {"name": "Cabin Type", "value": "First Class", "inline": False},
                    ],
                    "footer": {
                        "text": "American Airlines Price Monitor",
                        "icon_url": "https://static.dezeen.com/uploads/2013/01/dezeen_American-Airlines-logo-and-livery_4a.jpg"
                    },
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # UTC timestamp
                }
            ]
        }
        
        # Add origin/destination fields if available
        if data:
            if 'originAirportCode' in data:
                embed["embeds"][0]["fields"].append({"name": "Origin", "value": data.get('originAirportCode'), "inline": True})
            if 'destinationAirportCode' in data:
                embed["embeds"][0]["fields"].append({"name": "Destination", "value": data.get('destinationAirportCode'), "inline": True})
        
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.discord_webhook, data=json.dumps(embed), headers=headers)
            if response.status_code == 204:
                logging.info(f"Discord notification sent successfully for {confirmation_code}!")
            else:
                logging.error(f"Failed to send notification for {confirmation_code}. Status code: {response.status_code}, Response: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Failed to send Discord notification for {confirmation_code}: {e}")

if __name__ == '__main__':
    logging.info("Starting price monitor...")
    monitor = Monitor()
    monitor.check_price()
