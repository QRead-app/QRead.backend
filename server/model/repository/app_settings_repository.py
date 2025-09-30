from ..tables import AppSettings, Book, BookCondition
from .base_repository import BaseRepository
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

class AppSettingsRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_setting(
        self, 
        key: str | None
    ) -> list[AppSettings]:
        stmt = select(AppSettings)

        filters = []
        if key is not None:
            filters.append(AppSettings.key.like(f"%{key}%"))

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()

    def insert_setting(
        self, 
        key: str,
        value: str
    ) -> AppSettings:
        setting = AppSettings(key = key, value = value)
        self.session.add(setting)
        
        return setting

    def delete_setting(self, setting: AppSettings) -> None:
        self.session.delete(setting)  

    def truncate_table(self) -> None:
        self.session.execute(text("TRUNCATE TABLE app_settings RESTART IDENTITY CASCADE"))