from server.model.tables import AccountType, Book, BookCondition, User

test_borrower = User(
    name = "test_borrower",
    email = "test_borrower@email.com",
    password = "test_borrower",
    account_type = AccountType.BORROWER,
)

test_borrower_2 = User(
    name = "test_borrower_2",
    email = "test_borrower_2@email.com",
    password = "test_borrower_2",
    account_type = AccountType.BORROWER,
)

test_librarian = User(
    name = "test_librarian",
    email = "test_librarian@email.com",
    password = "test_librarian",
    account_type = AccountType.LIBRARIAN,
)

test_admin = User(
    name = "test_admin",
    email = "test_admin@email.com",
    password = "test_admin",
    account_type = AccountType.ADMIN,
)

test_book = Book(
    title = "test_title",
    description = "test_description",
    author = "test_author",
    condition = BookCondition.FAIR
)