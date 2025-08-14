from datetime import datetime
from ..tables import BookReturn
from .base_repository import BaseRepository
from sqlalchemy import select, text
from sqlalchemy.orm import Session

class BookReturnRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_book_return(
        self, 
        id: int | None = None, 
        book_transaction_id: int | None = None, 
        date: datetime | None = None, 
        librarian_id: int | None = None, 
    ) -> list[BookReturn]:
        stmt = select(BookReturn)

        filters = []
        if id is not None:
            filters.append(BookReturn.id == id)
        if book_transaction_id is not None:
            filters.append(BookReturn.book_transaction_id == book_transaction_id)
        if date is not None:
            filters.append(BookReturn.date == date)
        if librarian_id is not None:
            filters.append(BookReturn.librarian_id == librarian_id)

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()

    def insert_book_return(
        self, 
        book_transaction_id: int, 
        librarian_id: int
    ) -> BookReturn:
        bookreturn = BookReturn(
            book_transaction_id = book_transaction_id,
            librarian_id = librarian_id
        )
        self.session.add(bookreturn)

        return bookreturn
    
    def truncate_table(self) -> None:
        self.session.execute(text("TRUNCATE TABLE book_return CASCADE"))