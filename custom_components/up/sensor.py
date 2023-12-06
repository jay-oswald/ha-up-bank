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

    async_add_entities(Account(coordinator, coordinator.data[account]) for account in coordinator.data)

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
            async with async_timeout.timeout(20):
                return await self.api.getAccounts()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    

class Account(CoordinatorEntity, NumberEntity):
    account = {}
    def __init__(self, coordinator, account):
        super().__init__(coordinator, context=account)
        self.setValues(account)

    def setValues(self, account):
        _LOGGER.warning(account)
        self.account = account
        self._attr_unique_id = "up_" + account.id
        self._attr_name = account.name
        self.balance = account.balance
        self._state = account.balance
        self.id = account.id

    @callback
    def _handle_coordinator_update(self) -> None:
        self.setValues(self.coordinator.data[self.id])
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

    
