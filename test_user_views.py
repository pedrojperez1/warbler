"""User views tests."""

# run these tests with:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserViewsTestCase(TestCase):
    """Tests for User views"""
    def setUp(self):
        """set up each test"""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(email="test@test.com", username="testuser", password="HASHED_PASSWORD")
        u2 = User(email="test2@test.com", username="testuser2", password="HASHED_PASSWORD")
        u3 = User(email="test3@test.com", username="testuser3", password="HASHED_PASSWORD")
    
        u.id = 100
        u2.id = 200
        u3.id = 300
        u.following.append(u2)
        u2.following.append(u)

        db.session.add_all([u, u2, u3])
        db.session.commit()


    def tearDown(self):
        """clean up bad transactions"""
        db.session.rollback()

    def test_users_list(self):
        """Test /users route"""
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)

    def test_users_detail(self):
        """Test /users/<int:user_id> route"""
        with app.test_client() as client:
            resp = client.get('/users/100')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)

    def test_users_following_no_login(self):
        """Test /users/<int:user_id>/following"""
        with app.test_client() as client:
            resp = client.get('/users/100/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
            

    def test_users_followers_no_login(self):
        """Test /users/<int:user_id>/followers"""
        with app.test_client() as client:
            resp = client.get('/users/100/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_users_following_with_login(self):
        """Test /users/<int:user_id>/following"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 100 # log in
            
            resp = client.get('/users/100/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser2', html)

    def test_users_followers_with_login(self):
        """Test /users/<int:user_id>/followers"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 100 # log in
            
            resp = client.get('/users/100/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser2', html)
    
    def test_users_add_follow_no_login(self):
        """Test /users/follow/<int:follow_id>"""
        with app.test_client() as client:

            resp = client.post('/users/follow/300', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
            

    def test_users_add_follow_with_login(self):
        """Test /users/follow/<int:follow_id>"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 100 # log in

            resp = client.post('/users/follow/300', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser3', html)

            
            