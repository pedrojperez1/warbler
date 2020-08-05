"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        try:
            db.session.query(User).delete()
            db.session.query(Message).delete()
        except:
            db.session.rollback()
        
        self.client = app.test_client()

    def tearDown(self):
        """tear down sample user"""
        try:           
            db.session.query(User).delete()
            db.session.query(Message).delete()
        except:
            db.session.rollback()

    def test_message_model(self):
        """Make sure basic message model works"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
        message = Message(text='test message', user_id=u.id)
        db.session.add(message)
        db.session.commit()

        message2 = Message(text='second message', user_id=u.id)
        db.session.add(message2)
        db.session.commit() 

        self.assertEqual(len(u.messages), 2)

    def test_null_text(self):
        """Make sure text cannot be missing"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
        with self.assertRaises(IntegrityError):
            no_text_message = Message(user_id=u.id)
            db.session.add(no_text_message)
            db.session.commit()
            
    def test_null_user_id(self):
        """Make sure user_id cannot be missing"""
        with self.assertRaises(IntegrityError):
            no_user_message = Message(text='hello!')
            db.session.add(no_user_message)
            db.session.commit()

        