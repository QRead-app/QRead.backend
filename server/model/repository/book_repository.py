from ..tables import Book, BookCondition
from .base_repository import BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session

class BookRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)
    
    def get_book(
        self, 
        id: int | None = None, 
        title: str | None = None, 
        description: str | None = None, 
        author: str | None = None, 
        condition: BookCondition | None = None, 
    ) -> list[Book] | None:
        stmt = select(Book)

        filters = []
        if id is not None:
            filters.append(Book.id == id)
        if title is not None:
            filters.append(Book.title == title)
        if description is not None:
            filters.append(Book.description == description)
        if author is not None:
            filters.append(Book.author == author)
        if condition is not None:
            filters.append(Book.condition == condition)

        if filters: 
            stmt = stmt.where(*filters)

        return self.session.execute(stmt).scalars().all()


    def insert_book(self, title: str, description: str, author: str, condition: BookCondition) -> Book:
        book = Book(title = title, description = description, author = author, condition = condition)
        self.session.add(book)

        return book

    def delete_book(self, book: Book) -> None:
        self.session.delete(book)  