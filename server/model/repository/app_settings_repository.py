from ..tables import AppSettings, Book, BookCondition
from .base_repository import BaseRepository
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

class AppSettingsRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_setting(
        self, 
        key: str
    ) -> list[AppSettings]:
        return self.session.execute(
            select(AppSettings).where(AppSettings.key == key)
        ).scalars().all()

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
        self.session.execute(text("TRUNCATE TABLE app_settings CASCADE"))