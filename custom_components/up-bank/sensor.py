import logging
from datetime import timedelta
import async_timeout
from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import callback

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    up = hass.data[DOMAIN][config_entry.entry_id]

    coordinator = UpCoordinator(hass, up)

    await coordinator.async_config_entry_first_refresh()

    entities = [];
    for account_id in coordinator.data["accounts"]:
        entities.append(Account(coordinator, coordinator.data["accounts"][account_id]))
    
    individual_balance = coordinator.data['totals']['individual']['balance']
    individual_id = coordinator.data['totals']['individual']['id']
    entities.append(TotalSavings(
        coordinator,
        'individual',
        individual_balance,
        coordinator.data['accounts'][individual_id]
        ))

    joint_balance = coordinator.data['totals']['joint']['balance']
    joint_id = coordinator.data['totals']['joint']['id']
    if(joint_id != ''):
        entities.append(TotalSavings(
            coordinator,
            'joint',
            joint_balance,
            coordinator.data['accounts'][joint_id]
            ))
    

    async_add_entities(entities)

class UpCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, api):
        super().__init__(
            hass,
            _LOGGER,
            name="UP Coordinator",
            update_interval = timedelta(hours=1)
        )

        self.api = api

    async def _async_update_data(self):
        try:
            return await self.get_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        
    async def get_data(self):
        data = {}
        data['accounts'] = await self.api.getAccounts()
        joint = 0
        joint_id = ''
        individual = 0
        individual_id = ''
        for account_id in data['accounts']:
            account = data['accounts'][account_id]
            match account.accountType:
                case 'SAVER':
                    if account.ownership == "JOINT":
                        joint += float(account.balance)
                    else:
                        individual += float(account.balance)
                case 'TRANSACTIONAL':
                    if account.ownership == "JOINT":
                        joint_id = account.id
                    else:
                        individual_id = account.id
        data['totals'] = {
            'joint': {
                'balance': joint,
                'id': joint_id
            },
            'individual': {
                'balance': individual,
                'id': individual_id
            }
        }
        return data;
    

class Account(CoordinatorEntity, NumberEntity):
    account = {}
    def __init__(self, coordinator, account):
        super().__init__(coordinator, context=account)
        self.setValues(account)

    def setValues(self, account):
        self.account = account
        self._attr_unique_id = "up_" + account.id
        self._attr_name = account.name
        self.balance = account.balance
        self._state = account.balance
        self.id = account.id

    @callback
    def _handle_coordinator_update(self) -> None:
        self.setValues(self.coordinator.data['accounts'][self.id])
        self.async_write_ha_state()

    @property
    def device_class(self):
        return NumberDeviceClass.MONETARY
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": self.account.name,
            "manufacturer": self.account.ownership,
            "model": self.account.accountType
        }

    @property
    def available(self) -> bool:
        return True
    
    @property
    def state(self):
        return self.balance
    
    @property
    def mode(self):
        return 'box'
    
    @property
    def native_step(self):
        return 0.01

    
class TotalSavings(CoordinatorEntity, NumberEntity):
    account = {}
    def __init__(self, coordinator, type, balance, account):
        super().__init__(coordinator, context=account)
        self.setValues(balance)
        self.type = type
        self._attr_unique_id = "up_total_savings_" + self.type
        self.account = account
        self._attr_name = "Total " + self.type + " savings"
        

    def setValues(self, balance):
        self.balance = balance
        self._state = balance
        

    @callback
    def _handle_coordinator_update(self) -> None:
        self.setValues(self.coordinator.data['totals'][self.type]['balance'])
        self.async_write_ha_state()

    @property
    def device_class(self):
        return NumberDeviceClass.MONETARY
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "up_" + self.account.id)},
            "name": self.account.name,
            "manufacturer": self.account.ownership,
            "model": self.account.accountType
        }

    @property
    def available(self) -> bool:
        return True
    
    @property
    def state(self):
        return self.balance
    
    @property
    def mode(self):
        return 'box'
    
    @property
    def native_step(self):
        return 0.01