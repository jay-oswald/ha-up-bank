import aiohttp
import logging
_LOGGER = logging.getLogger(__name__)

base = "https://api.up.com.au/api/v1"

class UP:
    api_key = "";
    def __init__(self, key):
        self.api_key = key;

    async def call(self, endpoint, data = {}, method="get"):
        headers = { "Authorization": "Bearer " + self.api_key}
        match method:
            case "get":
                async with aiohttp.ClientSession(headers=headers) as session:
                    async with session.get(base + endpoint) as resp:
                        resp.data = await resp.json()
                        return resp



    async def test(self, api_key) -> bool:
        self.api_key = api_key
        result = await self.call("/util/ping")
        
        return result.status == 200
    
    async def getAccounts(self):
        result = await self.call('/accounts')
        if(result.status != 200):
            return False

        accounts = {};
        for account in result.data['data']:
            details = BankAccount(account)
            accounts[details.id] = details
                    
        return accounts


class BankAccount:
    def __init__(self, data):
        self.name = data['attributes']['displayName']
        self.balance = data['attributes']['balance']['value']
        self.id = data['id']
        self.createdAt = data['attributes']['createdAt']
        self.accountType = data['attributes']['accountType']
        self.ownership = data['attributes']['ownershipType']