from server.model.tables import AccountState, AccountType, Book, BookCondition, User
from server.model.seed.seeds import images

borrower = User(
    name = "borrower",
    email = "borrower@email.com",
    password = "borrower",
    account_type = AccountType.BORROWER,
)

borrower_deleted = User(
    name = "borrower_deleted",
    email = "borrower_deleted@email.com",
    password = "borrower_deleted",
    account_type = AccountType.BORROWER,
    account_state = AccountState.DELETED
)

borrower_suspended = User(
    name = "borrower_suspend",
    email = "borrower_suspend@email.com",
    password = "borrower_suspend",
    account_type = AccountType.BORROWER,
    account_state = AccountState.SUSPENDED
)

borrower_2 = User(
    name = "borrower_2",
    email = "borrower_2@email.com",
    password = "borrower_2",
    account_type = AccountType.BORROWER,
)

librarian = User(
    name = "librarian",
    email = "librarian@email.com",
    password = "librarian",
    account_type = AccountType.LIBRARIAN,
)

librarian_deleted = User(
    name = "librarian_deleted",
    email = "librarian_deleted@email.com",
    password = "librarian_deleted",
    account_type = AccountType.LIBRARIAN,
    account_state = AccountState.DELETED
)

librarian_suspended = User(
    name = "librarian_suspended",
    email = "librarian_suspended@email.com",
    password = "librarian_suspended",
    account_type = AccountType.LIBRARIAN,
    account_state = AccountState.SUSPENDED
)

admin = User(
    name = "admin",
    email = "admin@email.com",
    password = "admin",
    account_type = AccountType.ADMIN,
)

admin_deleted = User(
    name = "admin_deleted",
    email = "admin_deleted@email.com",
    password = "admin_deleted",
    account_type = AccountType.ADMIN,
    account_state = AccountState.DELETED
)

admin_suspended = User(
    name = "admin_suspended",
    email = "admin_suspended@email.com",
    password = "admin_suspended",
    account_type = AccountType.ADMIN,
    account_state = AccountState.SUSPENDED
)

book = Book(
    title = "title",
    description = "description",
    author = "author",
    condition = BookCondition.FAIR,
    image = images[0]
)