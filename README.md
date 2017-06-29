# WallAppBackend
Django backend for TSL hiring assignment

Instructions for running

First install the dependencies

Python 3 is required for this to install python 3 through homebrew run:

`brew install python3`

If you don't have homebrew:

`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

If pip is not already installed:

`sudo easy_install pip`

Then

`sudo pip3 install django`

`sudo pip3 install djangorestframework`

`sudo pip3 install django-sslserver`

`sudo pip3 install django-secure`

`sudo pip3 install coreapi-cli`

Next download it

`cd ~`

`git clone https://github.com/mddrill/WallAppBackend/`

Then run the unit tests

`cd ~/WallAppBackend`

`python3 manage.py test`

And run it

`python3 manage.py runserver`

It should now be running on `http://127.0.0.1:8000/`

I was using `httpie` to send http requests to the server to install httpie:

`brew install httpie`

To create an account run `http POST http://127.0.0.1:8000/accounts/ username=:"<username>" password="<password>" email="<email>"`

You can now submit posts at `http://127.0.0.1:800/post/` after logging in through the django browser tool

The unit tests should confirm that the email sending is working, if you want to test it out with a real email, you can uncomment this block in settings.py:

    '''EMAIL_USE_TLS = True
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = ''
    EMAIL_HOST_PASSWORD = '
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    '''
    
and replace the email host user and password with a gmail account. Be sure to allow emails from unsecure apps in your account by following the instructions here https://support.google.com/accounts/answer/6010255?hl=en

Now to test it with the iOS frontend you will have to run the backend with ssl like so:

`python3 manage.py runsslserver`
