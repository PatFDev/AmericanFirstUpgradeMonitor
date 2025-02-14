# American Airlines Price Monitor

This script monitors upgrade prices for American Airlines flights and sends notifications when the price changes.

## Features
- Fetches the upgrade price to First Class from the American Airlines API.
- Monitors for price changes at regular intervals.
- Sends notifications via Discord webhook when a price change is detected.

## Requirements
- Python 3.x
- `requests` library
- `.env` file with the following variables:
  - `CONFIRMATION_CODE`: Your AA confirmation code.
  - `DISCORD_WEBHOOK`: Your Discord webhook URL for notifications.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/PatFDev/AmericanFirstUpgradeMonitor.git
   cd AmericanFirstUpgradeMonitor
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add:
   ```sh
   CONFIRMATION_CODE=your_confirmation_code
   DISCORD_WEBHOOK=your_discord_webhook_url
   ```

## Usage
Run the script:
```sh
python monitor.py
```

## Notes
- The script will check the upgrade price every 60 seconds by default.
- Stop the script with `CTRL+C`.

