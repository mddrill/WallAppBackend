# WallAppBackend
Django backend for Facebook-like Wall App
Uses
```
Python 3
Django 1.1
Django-sslserver
```

Instructions for running

Python 3 is required for this, to install python 3 through homebrew run:
```
brew install python3
```

If you don't have homebrew:
```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Next download the repo
```
cd ~
git clone https://github.com/mddrill/WallAppBackend/
cd ~/WallAppBackend
```

Then create the virtual environment
```
virtualenv -p python3 venv
source venv/bin/activate
```

Then install the dependencies through requirements.txt
```
pip install -r requirements.txt
```

Now create the database
```
python manage.py makemigrations
python manage.py migrate
```

Then run the unit tests
```
python manage.py test
```

And run the it on localhost
```
python manage.py runserver
```

You can view the posts without authenticating
```
curl --request GET http://127.0.0.1:8000/post/
```

You can submit a post after creating an account
```
curl --data '{"username": "testuser", "password": "testpassword", "email": "test@testing.com"}' \
--header "Content-Type:application/json" \
--header "Accept: application/json" \
http://127.0.0.1:8000/accounts/
```

And getting the token
```
curl --data '{"username": "testuser", "password": "testpassword"}' \
--header "Content-Type:application/json" \
--header "Accept: application/json" \
http://127.0.0.1:8000/api-token-auth/
```

This will return a token which you can use to authenticate your post
```
curl --data '{"text": "testing123"}' \
--header "Content-Type:application/json" \
--header "Accept: application/json" \
--header "Authorization: Token <token>" \
http://127.0.0.1:8000/post/
```
The post should now be visible 
```
curl http://127.0.0.1:8000/post/
```

You can also edit and delete the post

To edit
```
curl --data '{"text": "new text"}'  \
--header "Content-Type:application/json" \
--header "Accept: application/json" \
--header "Authorization: Token <token>" \
--request PATCH http://127.0.0.1:8000/post/<post id>/
```

You can get the post id by reading the posts with `curl http://127.0.0.1:8000/post/` Assuming this is your first post, the id will be 1

To delete
```
curl --header "Content-Type:application/json" \
--header "Accept: application/json" \
--header "Authorization: Token <token>" \
--request DELETE http://127.0.0.1:8000/post/<post id>/
```

Now if you run `curl http://127.0.0.1:8000/post/` the post will be gone


The unit tests should confirm that the email sending is working. If you want to test it out with a real email, you can uncomment this block in settings.py:

    '''EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = '
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    '''
    
and replace the email host user and password with a gmail account. Be sure to allow emails from unsecure apps in your account by following the instructions here https://support.google.com/accounts/answer/6010255?hl=en

Now to test it with the iOS frontend follow the instructions in the README
https://github.com/mddrill/WallAppiOS
