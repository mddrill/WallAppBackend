from post.models import Post
from django.contrib.auth.models import User
from django.test import Client
from datetime import datetime, timezone
from rest_framework import status
from WallApp.test_utils import *
from rest_framework.test import APITestCase
import json

global N_TEST_USERS
global USERNAMES
global EMAILS
global PASSWORDS
global ADMIN_USERNAME
global ADMIN_PASSWORD
global ADMIN_EMAIL
global POSTS

# Test Models

'''class PostTestCase(TestCase):

    """
    Test that posts have the correct text after creation
    """

    TEXT_1 = 'user1\'s text'
    TEXT_2 = 'user2\'s text'
    TEXT_3 = 'user3\'s text'

    def setUp(self):
        self.user1 = User.objects.create_superuser('user1', 'user1@email.com', 'password1')
        self.user2 = User.objects.create_superuser('user2', 'user1@email.com', 'password2')
        self.user3 = User.objects.create_superuser('user3', 'user1@email.com', 'password3')

        Post.objects.create(author=self.user1, text=PostTestCase.TEXT_1)
        Post.objects.create(author=self.user2, text=PostTestCase.TEXT_2)
        Post.objects.create(author=self.user3, text=PostTestCase.TEXT_3)

    def test_posts(self):
        self.post1 = Post.objects.get(author=self.user1)
        self.assetEqual(PostTestCase.Text_1, self.post1.text)

        self.post2 = Post.objects.get(author=self.user2)
        self.assetEqual(PostTestCase.Text_2, self.post2.text)

        self.post3 = Post.objects.get(author=self.user3)
        self.assetEqual(PostTestCase.Text_3, self.post3.text)'''


# Test With Client

class PostTest(APITestCase):
    """
    All tests related to posting to the post
    """

    def setUp(self):
        """
        Set up tests
        """
        self.client = Client()

        self.assertEqual(N_TEST_USERS, len(USERNAMES), 'USERNAMES should be N_TEST_USERS length')
        self.assertEqual(N_TEST_USERS, len(EMAILS), 'EMAILS should be N_TEST_USERS length')
        self.assertEqual(N_TEST_USERS, len(PASSWORDS), 'PASSWORDS should be N_TEST_USERS length')
        self.assertEqual(N_TEST_USERS, len(POSTS), 'POSTS should be N_TEST_USERS length')

        self.users = []
        #create test users
        for i in range(N_TEST_USERS):
            self.users += [User.objects.create_user(username=USERNAMES[i],
                                              email=EMAILS[i],
                                              password=PASSWORDS[i])]

        User.objects.create_superuser(username=ADMIN_USERNAME, email=ADMIN_EMAIL, password=ADMIN_PASSWORD)

        self.test_posts = []
    
    def tearDown(self):
        self.test_posts = []
        Post.objects.all().delete()
        
    def create_test_posts(self):
        """
        Create some test posts, this can't be in setup because test_create_post creates posts a different way
        """
        self.test_posts = []
        for i in range(N_TEST_USERS):
            self.test_posts += [Post.objects.create(author=self.users[i], text=POSTS[i])]

        
    def test_post_pks(self):
        return [test_post.pk for test_post in self.test_posts]

    def test_get_post(self):
        """
        Make sure that GET method works even for anonymous users
        """
        # Create test posts
        self.create_test_posts()

        # Issue a GET request.
        response = self.client.get('/post/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK, 'Could not get the list of posts')

        # Check that there are the right number of posts
        self.assertEqual(response.json()['count'], len(self.test_posts), 'Did not get the right number of posts')

        # Check that posts contain the right info
        for i in range(len(self.test_posts)):
            self.assertEqual(response.json()['results'][i]['text'], self.test_posts[i].text, 'Post did not have the right text')
            self.assertEqual(response.json()['results'][i]['author'], str(self.test_posts[i].author), 'Post did not have the right author')

    def test_create_post(self):
        """
         Make sure the POST method only works when user is logged in
        """
        # First try with no user logged in (this should throw a value error because it will try and assign an anonymous user to the post)
        response = self.client.post('/post/', {'text' : 'this text should not go through because no user is logged in'})
        # Check that the response is 403 Forbidden.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN , 'Was able to post to the post without logging in')

        # Next try with three test users logged in and check that response is 200 OK and text and published time is accurate
        for i in range(N_TEST_USERS):
            # Log user  in
            logged_in = self.client.login(username=USERNAMES[i], password=PASSWORDS[i])
            # Check that we're logged in
            self.assertTrue(logged_in, 'Error logging in with test user number {}'.format(i))
            # Post text
            response = self.client.post('/post/', {'text' : POSTS[i]})
            # Check that response is CREATED
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Could not create post number {}'.format(i))
            # Check that text is accurate
            post = Post.objects.get(author=self.users[i])
            self.assertEqual(POSTS[i], post.text, 'Post number {} did not have the right text'.format(i))
            # Check that current time is not before posted_at time, and not more than 30 seconds after
            now = datetime.now(timezone.utc)
            time_difference = now - post.posted_at
            time_difference_mins, time_difference_secs = divmod(time_difference.days * 86400 + time_difference.seconds, 60)
            self.assertEqual(time_difference_mins, 0, 'Incorrect posted_at time, the post says it was posted at a time that is in the future')
            self.assertTrue(time_difference_secs < 30, 'Either incorrect posted_at time, or the post took longer than 30 seconds to be posted')

    def test_delete_post(self):
        """
        Make sure that users can only delete their own posts and admins can delete any post
        """
        # Create test posts
        self.create_test_posts()

        # Try to delete them without logging in (should get 403 Forbidden)
        for test_post in self.test_posts:
            response = self.client.delete('/post/{}/'.format(test_post.pk))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Was able to delete a post without logging in')

        for i in range(N_TEST_USERS):
            # login as user and try to delete all posts
            logged_in = self.client.login(username=USERNAMES[i], password=PASSWORDS[i])
            self.assertTrue(logged_in, 'Error logging in with test user number {}'.format(i))
            # Try and delete their posts (we have to start indexing at i because the posts before i have been deleted)
            for test_post in self.test_posts[i:]:
                # If pk is from logged in user, make sure that delete is successful
                if test_post.author == self.users[i]:
                    response = self.client.delete('/post/{}/'.format(test_post.pk))
                    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Test user was not able to delete a post that belonged to it')
                # Otherwise delete should fail
                else:
                    response = self.client.delete('/post/{}/'.format(test_post.pk))
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Test user was able to delete a post that did not belong to it')

        # Check that admins can delete any post
        # Create test posts
        self.create_test_posts()

        # Try and delete posts as admin, all should succeed
        logged_in = self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        self.assertTrue(logged_in, 'Error logging in with test admin user')

        for test_post in self.test_posts:
            response = self.client.delete('/post/{}/'.format(test_post.pk))
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, 'Was not able to delete a post as admin')
        
        
    def test_patch_post(self):
        """
        Make sure that only users can edit their own posts
        """
        # Create test posts
        self.create_test_posts()

        NEW_TEXT = 'new blah'

        # Try and edit their posts
        for test_post in self.test_posts:
            response = self.client.patch('/post/{}/'.format(test_post.pk),
                                         json.dumps({'text': NEW_TEXT}),
                                         content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Was able to edit a post without logging in')

        for i in range(N_TEST_USERS):
            # login as user and try to edit all posts
            logged_in = self.client.login(username=USERNAMES[i], password=PASSWORDS[i])
            self.assertTrue(logged_in, 'Error logging in with test user number {}'.format(i))
            # Try and edit their posts
            for test_post in self.test_posts:
                # If pk is from logged in user, make sure that patch is successful
                if test_post.author == self.users[i]:
                    response = self.client.patch('/post/{}/'.format(test_post.pk),
                                                 json.dumps({'text': NEW_TEXT}),
                                                 content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)#'Test user was not able to edit a post that belonged to it')
                # Otherwise patch should fail
                else:
                    response = self.client.patch('/post/{}/'.format(test_post.pk),
                                                 json.dumps({'text': NEW_TEXT}),
                                                 content_type='application/json')
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 'Test user was able to edit a post that did not belong to it')

        # Try and edit posts as admin, all should fail
        logged_in = self.client.login(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        self.assertTrue(logged_in, 'Error logging in with test admin user')

        for test_post in self.test_posts:
            response = self.client.patch('/post/{}/'.format(test_post.pk),
                                         json.dumps({'text': NEW_TEXT}),
                                         content_type='application/json')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                             'Was able to edit a user\'s post as admin')