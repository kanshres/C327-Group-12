import unittest
from sqlalchemy import exc
from qbay import database
from qbay.review import Review
from qbay.user import User
from qbay.listing import Listing
from qbay.transaction import Transaction, TransactionStatus
from qbay.wallet import Wallet, BankingAccount
from qbay.database import db, app
import pytest


"""
This file defines the testing for implemented data models
"""


class UnitTest(unittest.TestCase):

    def test_user(self):
        user = User()

        user.username = "KanchShres"
        assert user.username == "KanchShres"

        user.email = "19ks62@queensu.ca"
        assert user.email == "19ks62@queensu.ca"

        user.password = "Password123@!#&$^&*"
        assert user.password == "Password123@!#&$^&*"

        test_wall = Wallet()
        user.wallet = test_wall
        assert user.wallet == test_wall

        test_rev = Review()
        user.add_review(test_rev)
        assert user.reviews[0] == test_rev

    def test_review(self):
        review = Review()

        review.id = 1
        assert review.id == 1

        review.date_posted = "2022-09-21"
        assert review.date_posted == "2022-09-21"

        test_user = User()
        review.posting_user = test_user
        assert review.posting_user == test_user

        test_listing = Listing()
        review.listing = test_listing
        assert review.listing == test_listing

        review.rating = 3.4
        assert review.rating == 3.4

        review.comment = "hello world"
        assert review.comment == "hello world"

    def test_wallet_balance_transfer(self):
        bank_account = BankingAccount()
        user = User()
        wallet = user.create_wallet()
        user.wallet.bankingAccount = bank_account

        bank_account.add_balance(10000)
        assert user.wallet.bankingAccount.balance == 10000
        assert user.wallet.balance == 0

        user._wallet.transfer_balance(4000)
        assert user.wallet.bankingAccount.balance == 6000
        assert user.balance == 4000
        assert wallet.balance == 4000

        with self.assertRaises(ValueError):
            user.wallet.transfer_balance(-2000)

        with self.assertRaises(ValueError):
            bank_account.add_balance(-2000)

        assert user.balance == 4000
        assert bank_account.balance == 6000

    def test_transaction(self):
        transact = Transaction()
        transact.id = 50
        assert transact.id == 50

        test_user = User()
        transact.payer = test_user
        assert transact.payer == test_user

        test_user_2 = User()
        transact.payee = test_user_2
        assert transact.payee == test_user_2

        transact.amount = 50
        assert transact.amount == 50

        test_listing = Listing()
        transact.listing = test_listing
        assert transact.listing == test_listing

        transact.status = "transactionInProgress"
        assert transact.status == TransactionStatus.IN_PROGRESS

    def test_transaction_invalid_status(self):
        transact = Transaction()
        transact.status = TransactionStatus.COMPLETED
        assert transact.status == TransactionStatus.COMPLETED

        transact.status = "transactionCancelled"
        assert transact.status == TransactionStatus.CANCELLED

        with self.assertRaises(ValueError):
            transact.status = "Value error"

        with self.assertRaises(TypeError):
            transact.status = None

        with self.assertRaises(TypeError):
            transact.status = User()

    def test_listing(self):
        # Testing Initialization
        obj = Listing()
        # Testing param manipulation #
        obj.title = "4 Bed 2 Bath"
        obj.address = "Queen's University"
        obj.price = 8000.57
        obj._description = "Shittiest school to ever exist"
        obj.seller.username = "bob"
        r = []
        r1 = Review()
        r.append(r1)
        obj.reviews = r
        r2 = Review()
        obj.add_review(r2)

        assert obj.title == "4 Bed 2 Bath"
        assert obj.price == 8000.57
        assert obj.address == "Queen's University"
        assert obj._description == "Shittiest school to ever exist"
        assert obj.seller.username == "bob"
        assert obj.reviews == [r1, r2]

    def test_user_database(self):
        with app.app_context():
            db.drop_all()
            db.create_all()

        user = User("testUser", "user@example.ca", "password123")
        user.add_to_database()
        assert user.id == 1

        user2 = User("testUser2", "user@example.ca2", "password123")
        user2.add_to_database()
        assert user2.id == 2

        with self.assertRaises(exc.IntegrityError):
            user.add_to_database()

        user3 = User("testUser2", "user@example.ca2", "password123")
        with self.assertRaises(exc.DatabaseError):
            user3.add_to_database()

    def test_r1_1_user_register(self):
        """ Testing R1-1:
        Email and password cannot be empty.
        """

        assert User.register("u00", "test0@test.com", "Onetwo!") is True
        assert User.register("u01", "", "Onetwo!") is False
        assert User.register("u02", "test2@test.com", "") is False

    # need login function + database
    # def test_r1_2_user_register():
    #     """ Testing R1-2:
    #     User is uniquely identified by their user id.
    #     """

    #     user = login("test0@test.com", "Onetwo!")
    #     assert user is not None
    #     # might have to change later
    #     uuid_obj = UUID(user.id, version=4)
    #     assert str(uuid_obj) == user.id

    def test_r1_3_user_register(self):
        """ Testing R1-3:
        Email has to follow addr-spec defined in RFC 5322.
        """

        assert User.register("u01", "test.1@test.com", "Onetwo!") is True
        assert User.register("u02", "test2@test", "Onetwo!") is False
        assert User.register("u02", "test2@.com", "Onetwo!") is False
        assert User.register("u02", "@test.com", "Onetwo!") is False
        assert User.register("u02", "testing", "Onetwo!") is False
        assert User.register(
            "u02", "(Jon Test) test2@test.com", "Onetwo!") is False

    def test_r1_4_user_register(self):
        """ Testing R1-4:
        Password meets required complexity.
        """

        assert User.register("u02", "test2@test.com", "One23!") is True
        assert User.register("u03", "test3@test.com", "One2!") is False
        assert User.register("u03", "test3@test.com", "onetwo!") is False
        assert User.register("u03", "test3@test.com", "ONETWO!") is False
        assert User.register("u03", "test3@test.com", "Onetwo") is False

    def test_r1_5_user_register(self):
        """ Testing R1-5:
        User name is non-empty, alphanumeric-only, and spaces are allowed
        only if it is not as the prefix or suffix.
        """

        assert User.register("u03", "test3@test.com", "Onetwo!") is True
        assert User.register("User 04", "test4@test.com", "Onetwo!") is True
        assert User.register("", "test5@test.com", "Onetwo!") is False
        assert User.register("u05!", "test5@test.com", "Onetwo!") is False
        assert User.register("u05 ", "test5@test.com", "Onetwo!") is False
        assert User.register(" u05", "test5@test.com", "Onetwo!") is False

    def test_r1_6_user_register(self):
        """ Testing R1-6:
        User name length is longer 2 and less than 20 characters.
        """

        assert User.register("u05", "test5@test.com", "Onetwo!") is True
        assert User.register("u06ThisUsernameWork",
                             "test6@test.com", "Onetwo!") is True
        assert User.register("u07ThisUsernameWillNotWork",
                             "test7@test.com", "Onetwo!") is False
        assert User.register("u7", "test7@test.com", "Onetwo!") is False

    def test_r3_1_update_user(self):
        """ Testing R3-1:
        A user is only able to update his/her user name, user email,
        billing address, and postal code.
        """
        with database.app.app_context():
            db.drop_all()
            db.create_all()
        user = User("testUser", "user@example.ca", "password123")
        user.add_to_database()

        # Update username
        user.update_username("updatedUsername")
        assert user.database_obj.username == "updatedUsername"

        # Update user email
        user.update_email("updated@email.com")
        assert user.database_obj.email == "updated@email.com"

        # Update address
        user.update_billing_address("123 Update")
        assert user.database_obj.billing_address == "123 Update"

        # Update postal code
        user.update_postal_code("A1A1A1")
        assert user.database_obj.postal_code == "A1A1A1"

    def test_r3_2_r3_3_update_postal_code(self):
        """Testing R3-2: 
        postal code should be non-empty, alphanumeric-only,
        and no special characters such as !.
        """
        with database.app.app_context():
            db.drop_all()
            db.create_all()
        user = User("testUser", "user@example.ca", "password123")
        user.add_to_database()

        valid_postal_codes = ["a1a1a1", "A1A1A1",
                              "N1P0A0", "N1T9Z9", "V0C0A0", "V0C9Z9"]
        for i in valid_postal_codes:
            user.update_postal_code(i)
            user.database_obj.postal_code == i

        invalid_postal_codes = ["", "!C1Ajd", "a!a1a1",
                                "AAAAAA", "123904", "ASD2U1",
                                "1A2C3D", "D1C9E7"]
        for i in invalid_postal_codes:
            assert user.update_postal_code(i) is False

    def test_r3_4_update_username(self):
        with database.app.app_context():
            db.drop_all()
            db.create_all()
        user = User("testUser", "user@example.ca", "password123")
        user.add_to_database()

        valid_usernames = ["asdhjk", "userName",
                           "USERNAME", "user name", "123 1112 4902"]
        for i in valid_usernames:
            user.update_username(i)
            assert user.database_obj.username == i
        invalid_usernames = ["", " ASD", "! ASD",
                             "as", "1246789012317823678123678678904"]

        for i in invalid_usernames:
            assert user.update_username(i) is False

# need database to check existing emails
# def test_r1_7_user_register():
#     """ Testing R1-7:
#     If email has been used, operation failed.
#     """

#     assert register("u07", "test7@test.com", "Onetwo!") is True
#     assert register("u08", "test7@test.com", "Onetwo!") is False

# need database for rest
# def test_r1_8_user_register():
#     """ Testing R1-8:
#     Billing Address is empty at time of registration.
#     """

#     user = login("u00", "test0@test.com", "Onetwo!")
#     assert user is not None
#     assert user.billing_address == ""

# def test_r1_9_user_register():
#     """ Testing R1-9:
#     Postal Code is empty at time of registration.
#     """

#     user = login("u00", "test0@test.com", "Onetwo!")
#     assert user is not None
#     assert user.postal_code == ""

# def test_r1_10_user_register():
#     """ Testing R1-10:
#     Balance should be initialized as 100 at time of registration.
#     """

#     user = login("u00", "test0@test.com", "Onetwo!")
#     assert user is not None
#     assert user.balance == 100


def test_r2_1():
    """Test if user can log in using her/his email address and the 
    password.

    Note:
    User.login will return 0 if login success
    User.login will return 1 if login failure due to invalid username 
                                                            or password
    User.login will return 2 if login failure due to incorrect 
                                                username or password
    """
    with app.app_context():
        db.drop_all()
        db.create_all()

    bob = User()
    bob.email = "bob@gmail.com"
    bob.password = "Password123!"
    bob.add_to_database()

    fred = User()
    fred.email = "fred@gmail.com"
    fred.password = "Password321!"
    fred.add_to_database()

    assert User.login("bob@gmail.com", "Password123!") == 0
    assert User.login("fred@gmail.com", "Password321!") == 0
    assert User.login("bob@gmail.com", "IncorrectPassword123!") == 2
    assert User.login("fred@gmail.com", "Password123!") == 2


def test_r2_2():
    """Test that the login function should check if the supplied 
    inputs meet the same email/password requirements as above, before 
    checking the database.

    Note:
    User.login will return 0 if login success
    User.login will return 1 if login failure due to invalid username 
                                                            or password
    User.login will return 2 if login failure due to incorrect 
                                                   username or password
    """
    with app.app_context():
        db.drop_all()
        db.create_all()

    bob = User()
    bob.email = "bob@gmail.com"
    bob.password = "Password123!"
    bob.add_to_database()

    assert User.login("bob@gmail.com", "Password123!") == 0

    assert User.login("b.o.b.@gmail..com", "Password123!") == 1
    assert User.login("bob@gmail.com", "psw") == 1
    assert User.login("b.o.b.@gmail..com", "psw") == 1


if __name__ == "__main__":
    unittest.main()
