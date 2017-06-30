from django.contrib.auth.models import User
import json
from django.test import TestCase
from rest_framework import status
from WallApp.test_utils import *
from django.core import mail
from accounts.email_info import *
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


global WELCOME_EMAIL_SUBJECT
global WELCOME_EMAIL_MESSAGE
global COMPANY_EMAIL


global N_TEST_USERS
global USERNAMES
global EMAILS
global PASSWORDS
global ADMIN_USERNAME
global ADMIN_PASSWORD
global ADMIN_EMAIL


class AccountsTest(TestCase):
    """
    All tests related to registering and logging in to the site
    """

    def setUp(self):
        """
        Set up tests
        """
        self.client = APIClient()

        User.objects.create_superuser(username=ADMIN_USERNAME,
                                      email=ADMIN_EMAIL,
                                      password=ADMIN_PASSWORD)

    def tearDown(self):
        """
        Deletes all users to ensure that we are starting from scratch with each test
        """
        User.objects.all().delete()

    def register_test_users(self):
        """
        Registers three test users
        (This is different from setUp because test users will have to be registerd multiple times, setUp is called once 
        """
        self.assertEqual(N_TEST_USERS, len(USERNAMES), 'USERNAMES should be N_TEST_USERS length')
        self.assertEqual(N_TEST_USERS, len(EMAILS), 'EMAILS should be N_TEST_USERS length')
        self.assertEqual(N_TEST_USERS, len(PASSWORDS), 'PASSWORDS should be N_TEST_USERS length')
        self.assertEqual(N_TEST_USERS, len(POSTS), 'POSTS should be N_TEST_USERS length')

        # Register test users
        self.users = []
        for i in range(N_TEST_USERS):
            self.users += [User.objects.create_user(username=USERNAMES[i],
                                                     email=EMAILS[i],
                                                     password=PASSWORDS[i])]

    def login(self, username):
        token = Token.objects.get(user__username=username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def logout(self):
        self.client.credentials()

    def test_create_account(self):
        """
        Register users then assert that they can log in and their information is correct
        """
        # Register test users
        for i in range(N_TEST_USERS):
            response = self.client.post('/accounts/',
                                    {'username': USERNAMES[i], 'password': PASSWORDS[i],
                                     'email': EMAILS[i]})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Was unable to create an account')

            # Check that information is correct
            user = User.objects.get(username=USERNAMES[i])
            self.assertEqual(EMAILS[i], user.email, 'Account did not contain the correct email address after creation')

            #Check that the welcome email was sent
            self.assertEqual(len(mail.outbox), i+1, 'Outbox does not containt the correct number of emails, Email may not have been sent')
            self.assertEqual(mail.outbox[i].recipients()[0], EMAILS[i], 'Email was not sent to the correct email address')
            self.assertEqual(mail.outbox[i].subject, WELCOME_EMAIL_SUBJECT, 'Email was not sent with the right subject')
            self.assertEqual(mail.outbox[i].body, WELCOME_EMAIL_MESSAGE, 'Email was not sent with the right body')


    def test_get_account(self):
        """
        Test that users can only get their own information, but not others information
        """
        # Register test users
        self.register_test_users()

        # Try and get their information without logging in (should fail)
        response = self.client.get('/accounts/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK, 'Was able to view account list without logging in')
        for account in self.users:
            response = self.client.get('/accounts/{}/'.format(account.pk))
            self.assertNotEqual(response.status_code, status.HTTP_200_OK, 'Was able to view account details without logging in')

        for i in range(N_TEST_USERS):
            # login as user and try to access accounts
            self.login(USERNAMES[i])
            # Try and get their information
            response = self.client.get('/accounts/')
            self.assertNotEqual(response.status_code, status.HTTP_200_OK, 'Was able to view account list after logging in')
            for account in self.users:
                # If account belongs to the user that's logged it, get should be successful
                if account == self.users[i]:
                    response = self.client.get('/accounts/{}/'.format(account.pk))
                    self.assertEqual(response.status_code, status.HTTP_200_OK, 'Test user could not view it\'s own account details')
                # Otherwise get should fail
                else:
                    response = self.client.get('/accounts/{}/'.format(account.pk))
                    self.assertNotEqual(response.status_code, status.HTTP_200_OK, 'Test user was able to  view account details that did not belong to it')
            self.logout()

        # Try and view all accounts as admin (should fail in all cases)
        self.login(ADMIN_USERNAME)

        response = self.client.get('/accounts/')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK,
                         'Was able to view account list as admin')
        for account in self.users:
            response = self.client.get('/accounts/{}/'.format(account.pk))
            self.assertNotEqual(response.status_code, status.HTTP_200_OK,
                             'Was able to view account details as admin')

        self.logout()


    def test_delete_account(self):
        """
        Make sure that only users can delete their own accounts and admins can delete all accounts
        """
        # Register test users
        self.register_test_users()

        # Try and delete their accounts without logging in (should fail)
        for account in self.users:
            response = self.client.delete('/accounts/{}/'.format(account.pk))
            self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Was able to delete accounts without logging in')

        for i in range(N_TEST_USERS):
            # login as user and try to delete all accounts
            self.login(USERNAMES[i])
            # Try and delete their accounts (we have to start indexing at i because the users before i have been deleted)
            for account in self.users[i:]:
                # If account belongs to the user that's logged it, delete should be successful
                if account == self.users[i]:
                    response = self.client.delete('/accounts/{}/'.format(account.pk))
                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Test user was not able to delete it\'s own account')

                # Otherwise delete should fail
                else:
                    response = self.client.delete('/accounts/{}/'.format(account.pk))
                    self.assertNotEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Test user was able to delete an account that did not belong to it')
            self.logout()

        # Check that admins can delete any account
        # Register test users
        self.register_test_users()

        self.login(ADMIN_USERNAME)

        # Try and delete accounts as admin (should succeed in all cases)
        for account in self.users:
            response = self.client.delete('/accounts/{}/'.format(account.pk))
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Admin was not able to delete an account')

        self.logout()

    def test_patch_account(self):
        """
        Make sure that only users can edit their own accounts
        """
        # Register test users
        self.register_test_users()

        NEW_EMAIL = 'newemail@new.com'

        # Try and edit test users' information without logging in (should fail in all cases)
        for account in self.users:
            response = self.client.patch('/accounts/{}/'.format(account.pk),
                                         json.dumps({'email': NEW_EMAIL}),
                                         content_type='application/json')
            self.assertNotEqual(response.status_code, status.HTTP_200_OK, 'Was able to edit a user\'s account without logging in')

        # Try and edit test users' information after logging in
        # (should succeed when editing your own information, but fail when editing other users' information)
        for i in range(N_TEST_USERS):
            # login as user and try to edit all accounts
            self.login(USERNAMES[i])
            # Try and edit their accounts
            for account in self.users:
                # If account belongs to the user that's logged it, patch should be successful
                if account == self.users[i]:
                    response = self.client.patch('/accounts/{}/'.format(account.pk),
                                                 json.dumps({'email': NEW_EMAIL}),
                                                 content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)#'Test user was not able to edit it\'s own account')
                # Otherwise patch should fail
                else:
                    response = self.client.patch('/accounts/{}/'.format(account.pk),
                                                 json.dumps({'email': NEW_EMAIL}),
                                                 content_type='application/json')
                    self.assertNotEqual(response.status_code, status.HTTP_200_OK, 'Test user was able to edit an account that was it\'s own')
            self.logout()

        # Try and edit test users' information with admin account (should fail in all cases)
        self.login(ADMIN_USERNAME)

        # Try and delete accounts as admin (should succeed in all cases)
        for account in self.users:
            response = self.client.patch('/accounts/{}/'.format(account.pk),
                                         json.dumps({'email': NEW_EMAIL}),
                                         content_type='application/json')
            self.assertNotEqual(response.status_code, status.HTTP_200_OK,
                             'Admin was able to edit a user\'s account')
        self.logout()
