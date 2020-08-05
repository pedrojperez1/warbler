"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

from sqlalchemy.exc import IntegrityError

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Make sure repr method works"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        self.assertEqual(str(u), f"<User #{u.id}: testuser, test@test.com>")

    def test_follows(self):
        """Make sure is_following and is_followed_by methods work"""

        u1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )

        self.assertEqual(u1.is_following(u2), False)
        self.assertEqual(u2.is_followed_by(u1), False)

        u1.following.append(u2)
        db.session.add(u1)
        db.session.commit()

        self.assertEqual(u1.is_following(u2), True)
        self.assertEqual(u2.is_followed_by(u1), True)

    def test_signup_cls_method(self):
        """Make sure signup class method works"""
        u1 = User.signup(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD",
            image_url="www.image.com"
        )
        db.session.commit()
        queried_user = User.query.get(u1.id)
        self.assertEqual(str(queried_user), str(u1))
        with self.assertRaises(IntegrityError):
            fail_user = User.signup(
                email='email@email.com',
                username='user1',
                password='pass',
                image_url='www.image.com'
            )
            db.session.add(fail_user)
            db.session.commit()

    def test_authentication(self):
        """Make sure authentication method works"""
        fail_login_user = User.authenticate('user', 'pass')
        self.assertFalse(fail_login_user)

        u1 = User.signup(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD",
            image_url="www.image.com"
        )
        db.session.commit()

        success_login_user = User.authenticate('user1', 'HASHED_PASSWORD')
        self.assertEqual(success_login_user.username, u1.username)

        fail_pass = User.authenticate('user1', 'WRONG_PASSWORD')
        self.assertFalse(fail_pass)

        fail_username = User.authenticate('user2', 'HASHED_PASSWORD')
        self.assertFalse(fail_username)