"""Spook - Your homie."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.components.input_text import (
    CONF_INITIAL,
    CONF_MAX,
    CONF_MAX_VALUE,
    CONF_MIN,
    CONF_MIN_VALUE,
    CONF_PATTERN,
    DOMAIN,
    MODE_PASSWORD,
    MODE_TEXT,
    InputTextStorageCollection,
    _cv_input_text,
)
from homeassistant.const import CONF_ICON, CONF_MODE, CONF_NAME
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from ....services import AbstractSpookAdminService

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall

CONF_OBJECT_ID = "object_id"

CREATE_FIELDS = {
    vol.Required(CONF_NAME): vol.All(str, vol.Length(min=1)),
    vol.Optional(CONF_OBJECT_ID): cv.slug,
    vol.Optional(CONF_MIN, default=CONF_MIN_VALUE): vol.All(
        vol.Coerce(int), vol.Range(min=0, max=255)
    ),
    vol.Optional(CONF_MAX, default=CONF_MAX_VALUE): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=255)
    ),
    vol.Optional(CONF_INITIAL): cv.string,
    vol.Optional(CONF_ICON): cv.icon,
    vol.Optional(CONF_PATTERN): cv.string,
    vol.Optional(CONF_MODE, default=MODE_TEXT): vol.In([MODE_TEXT, MODE_PASSWORD]),
}


class SpookService(AbstractSpookAdminService):
    """Input text service to create a new helper on the fly."""

    domain = DOMAIN
    service = "create"
    schema = vol.All(vol.Schema(CREATE_FIELDS), _cv_input_text)

    async def async_handle_service(self, call: ServiceCall) -> None:
        """Handle the service call."""
        object_id = call.data.get(CONF_OBJECT_ID)
        data = {k: v for k, v in call.data.items() if k != CONF_OBJECT_ID}

        collection: InputTextStorageCollection = self.hass.data["websocket_api"][
            "input_text/list"
        ][0].__self__.storage_collection

        if object_id:
            if collection.id_manager.has_id(object_id):
                message = f"An input text with object ID '{object_id}' already exists"
                raise HomeAssistantError(message)
            original_get_suggested_id = collection._get_suggested_id  # noqa: SLF001
            collection._get_suggested_id = lambda info: object_id  # noqa: SLF001
            try:
                await collection.async_create_item(data)
            finally:
                collection._get_suggested_id = original_get_suggested_id  # noqa: SLF001
        else:
            await collection.async_create_item(data)
