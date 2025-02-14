# American Airlines Price Monitor

This script monitors upgrade prices for American Airlines flights and sends notifications when the price changes. It logs activity using Python's `logging` module to ensure visibility on the Render dashboard.

## Features
- Fetches the upgrade price from the American Airlines API.
- Monitors for price changes at regular intervals.
- Sends notifications via Discord webhook when a price change is detected.
- Logs all activities to Render for tracking.

## Requirements
- Python 3.x
- `requests` library
- `.env` file with the following variables:
  - `CONFIRMATION_CODE`: Your AA confirmation code.
  - `DISCORD_WEBHOOK`: Your Discord webhook URL for notifications.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/aa-price-monitor.git
   cd aa-price-monitor
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

## Logging
- The script uses Python's `logging` module to log events.
- Logs will be visible on the Render dashboard.
- Errors and significant updates will also be logged.

## Notes
- The script will check the upgrade price every 60 seconds by default.
- Stop the script with `CTRL+C`.

## License
MIT License

