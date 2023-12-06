import logging
from typing import Any
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
import voluptuous as vol
from .const import DOMAIN
from .up import UP

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    })
_LOGGER = logging.getLogger(__name__)

class UpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}
        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            try:
                up = UP(api_key)
                info = await up.test(api_key)

                if info:
                    return self.async_create_entry(title="UP", data=user_input)
                else:
                    errors[CONF_API_KEY] = "API key failed validation"
            except ConnectionError:
                _LOGGER.exception("Connection Error")
                errors[CONF_API_KEY] = "API Connection Error"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors[CONF_API_KEY] = "API Key not validated, unknown error"
                
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

