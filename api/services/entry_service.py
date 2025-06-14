from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

from api.repositories.postgres_repository import PostgresDB

logger = logging.getLogger("journal")

class EntryService:
    def __init__(self, db: PostgresDB):
        self.db = db
        logger.debug("EntryService initialized with PostgresDB client.")

    async def create_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a new entry."""
        logger.info("Creating entry")
        entry = await self.db.create_entry(entry_data)
        logger.debug("Entry created: %s", entry)
        return entry

    async def get_entries(self) -> List[Dict[str, Any]]:
        logger.info("Fetching entries")
        entries = await self.db.get_entries()
        logger.debug("Fetched %d entries", len(entries))
        return entries

    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        logger.info("Fetching entry %s", entry_id)
        entry = await self.db.get_entry(entry_id)
        if not entry:
            logger.warning("Entry %s not found", entry_id)
        return entry

    async def update_entry(self, entry_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing entry."""
        logger.info("Updating entry %s", entry_id)
        existing_entry = await self.db.get_entry(entry_id)
        if not existing_entry:
            raise ValueError(f"Entry {entry_id} not found")

        # Merge updated fields into existing data
        existing_data = existing_entry["data"]
        existing_data.update(updated_data)
        existing_data["updated_at"] = datetime.now(timezone.utc)

        await self.db.update_entry(entry_id, existing_data)
        logger.debug("Entry %s updated", entry_id)
        return existing_data

    async def delete_entry(self, entry_id: str) -> None:
        logger.info("Deleting entry %s", entry_id)
        await self.db.delete_entry(entry_id)
        logger.debug("Entry %s deleted", entry_id)

    async def delete_all_entries(self) -> None:
        logger.info("Deleting all entries")
        await self.db.delete_all_entries()
        logger.debug("All entries deleted")
