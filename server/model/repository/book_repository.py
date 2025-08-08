from ..tables import Book, BookCondition
from .base_repository import BaseRepository
from sqlalchemy import select, Row
from sqlalchemy.orm import Session

class BookRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_book_by_id(self, id: int) -> Book|None:
        return self.session.get(Book, id)
    
    def get_books_by_title(self, title: str) -> Row[Book]|None:
        return self.session.execute(
            select(Book)
                .where(Book.title == title)
        ).all()

    def insert_book(self, title: str, description: str, author: str, condition: BookCondition) -> Book:
        book = Book(title = title, description = description, author = author, condition = condition)
        self.session.add(book)

        return book

    def delete_book(self, book: Book) -> None:
        self.session.delete(book)  