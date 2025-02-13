import requests
import os
import dotenv
import json
import time

dotenv.load_dotenv()

URL = "https://www.aa.com/offers/bff/products"

PAYLOAD = {
    "metadata": {
        "clientId": "AACOM",
        "journeyPath": "INSTANT_UPSELL",
        "locale": "en_US",
        "cartId": ""
    },
    "recordLocator": os.getenv('CONFIRMATION_CODE'),
    "currency": "USD"
}

HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://www.aa.com',
    'referer': 'https://www.aa.com/reservation/view/find-your-trip',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
}

class Monitor:
    def __init__(self):
        self.price = self.get_price()
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        self.delay = 60  # seconds

        if not self.discord_webhook:
            raise ValueError("❌ ERROR: No Discord Webhook URL found in environment variables!")

    def get_price(self):
        """Fetch the upgrade price from AA's API."""
        try:
            response = requests.post(URL, headers=HEADERS, json=PAYLOAD)
            response.raise_for_status()
            data = response.json()

            teasers = data.get('teaser', [])
            for teaser in teasers:
                content = teaser.get('content', {})
                if content.get('cabinType') == 'FIRST':
                    price = content.get('offerPrice')
                    print(f"💰 Price to upgrade to First: ${price}")
                    return price
            return None
        except requests.RequestException as e:
            print(f"❌ ERROR: Failed to fetch price: {e}")
            return None

    def check_price(self):
        """Continuously check for price changes and send notifications."""
        try:
            while True:
                new_price = self.get_price()
                if new_price is not None and new_price != self.price:
                    print(f"📢 Price changed from {self.price} to {new_price}")
                    self.price = new_price
                    self.send_discord_embed()
                else:
                    print("⏳ Price has not changed.")

                time.sleep(self.delay)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user.")

    def send_discord_embed(self, title="✈️ Flight Upgrade Alert", description="New upgrade price detected!", color=0x5865F2):
        """Send a Discord embed notification when the price changes."""
        if not self.discord_webhook:
            print("⚠️ No Discord webhook URL found.")
            return
        
        embed = {
            "embeds": [
                {
                    "title": title,
                    "description": description,
                    "color": color,
                    "fields": [
                        {"name": "New Price", "value": f"${self.price}", "inline": True},
                        {"name": "Currency", "value": "USD", "inline": True},
                        {"name": "Cabin Type", "value": "First Class", "inline": False}
                    ],
                    "footer": {
                        "text": "American Airlines Price Monitor",
                        "icon_url": "https://upload.wikimedia.org/wikipedia/commons/9/9d/American_Airlines_Logo.svg"
                    },
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())  # UTC timestamp
                }
            ]
        }
        
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.discord_webhook, data=json.dumps(embed), headers=headers)
            if response.status_code == 204:
                print("✅ Discord notification sent successfully!")
            else:
                print(f"❌ Failed to send notification. Status code: {response.status_code}, Response: {response.text}")
        except requests.RequestException as e:
            print(f"❌ ERROR: Failed to send Discord notification: {e}")

if __name__ == '__main__':
    print("🚀 Starting price monitor...")
    monitor = Monitor()
    monitor.check_price()
