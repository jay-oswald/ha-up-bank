Home Assistant Up Bank Integration

This integration will fetch details about all of your UP accounts, for you to use how you want. At the moment it refreshes once an hour to update balances. Ideally I would like to receive webhooks and update in real-time.

Any feature requests feel free to vote or add a [discussion](https://github.com/jay-oswald/ha-up-bank/discussions) and any bugs create, or comment on an [issue](https://github.com/jay-oswald/ha-up-bank/issues)

# Installation
The easiest way is to install via HACS, see https://github.com/hacs/integration to install HACS if you haven't already.

1. Go to HACS on your home assistant site
2. Select Integrations
3. Top right click on the 3 dots, then Custom repositories
3. Enter this repository https://github.com/jay-oswald/ha-up-bank then select category integration and add
4. Explore and Download
5. Search for HA UP and install this integration
6. Restart Home Assistant
7. Go to regular integrations (not HACS)
8. Search for and add HA Up
9. Get your UP API key from: https://api.up.com.au/getting_started
10. Enter the API key on the config screen

# Development
I have included a docker-compose file with mapping, so make sure you have docker, and docker-compose installed. Then you can start it with `docker-compose up -d`. Every time you change the files you will need to restart the server inside the HA GUI for the changes to kick in.
