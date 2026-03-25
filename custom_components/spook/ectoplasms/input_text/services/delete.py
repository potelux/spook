"""Spook - Your homie."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.input_text import (
    DOMAIN,
    InputText,
    InputTextStorageCollection,
)
from homeassistant.exceptions import HomeAssistantError

from ....services import AbstractSpookEntityComponentService

if TYPE_CHECKING:
    from homeassistant.core import ServiceCall


class SpookService(AbstractSpookEntityComponentService[InputText]):
    """Input text service to delete a helper on the fly."""

    domain = DOMAIN
    service = "delete"
    schema = {}

    async def async_handle_service(
        self,
        entity: InputText,
        call: ServiceCall,
    ) -> None:
        """Handle the service call."""
        if not entity.editable:
            message = f"This input text is not editable: {entity.entity_id}"
            raise HomeAssistantError(message)

        collection: InputTextStorageCollection = self.hass.data["websocket_api"][
            "input_text/list"
        ][0].__self__.storage_collection
        await collection.async_delete_item(entity.unique_id)
