import datetime
import random
from google.cloud import datastore
import google.oauth2.id_token
from flask import Flask, render_template, request
from google.auth.transport import requests
from werkzeug.utils import redirect
import os

app = Flask(__name__)

datastore_client = datastore.Client()

firebase_request_adapter = requests.Request()


def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity


def createUserInfo(claims, username):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key=entity_key)
    entity.update({
        'email': claims['email'],
        'name': claims['name'],
        'username': username,
        'description': '',
        'followings': [],
        'followers': [],
        'tweet_list': []
    })
    datastore_client.put(entity)


def createTweet(claims, tweet, email):
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Tweets', id)
    entity = datastore.Entity(key=entity_key)
    date = datetime.datetime.now()
    entity.update({
        'tweet': tweet,
        'date': date,
        'creator': email
    })
    datastore_client.put(entity)
    return id


def retrieveTweet(user_info):
    tweet_ids = user_info['tweet_list']
    tweet_keys = []
    for i in range(len(tweet_ids)):
        tweet_keys.append(datastore_client.key('Tweets', tweet_ids[i]))
    tweet_list = datastore_client.get_multi(tweet_keys)
    return tweet_list


def addTweetToUser(user_info, id):
    tweet_keys = user_info['tweet_list']
    tweet_keys.append(id)
    user_info.update({
        'tweet_list': tweet_keys
    })
    datastore_client.put(user_info)


def retrieve_all_users():
    query = datastore_client.query(kind='UserInfo')
    all_keys = list(query.fetch())
    return all_keys


def retrieve_all_tweets():
    query = datastore_client.query(kind='Tweets')
    all_keys = list(query.fetch())
    return all_keys


# these functions below will be for rendering templates


@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    tweets = []
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info is None:
                return render_template('usernamePage.html', add=0)
            # tweets = retrieve_all_tweets()
            query = datastore_client.query(kind="Tweets")
            query.order = ["-date"]

            result = list(query.fetch())
            users = user_info['followings']
            users.append(user_info['email'])
            for tweet in result:
                if tweet['creator'] in users:
                    tweets.append(tweet)
        except ValueError as exc:
            error_message = str(exc)

    return render_template('index.html', user_data=claims, user_info=user_info,
                           tweets=tweets, error_message=error_message, bool=0)


@app.route('/home')
def home():
    return redirect('/')


@app.route('/get_username', methods=['POST'])
def get_username():
    error_message = None
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                          firebase_request_adapter)
    user_info = retrieveUserInfo(claims)
    users = retrieve_all_users()
    username = request.form['username']
    if ' ' in username:
        return render_template('usernamePage.html', add=2)
    for user in users:
        if user['username'] == username:
            return render_template('usernamePage.html', add=1)

    createUserInfo(claims, username)
    user_info = retrieveUserInfo(claims)

    return render_template('index.html', user_data=claims, user_info=user_info,
                           tweets=None, error_message=error_message, bool=0)


@app.route('/profile_page')
def profile_page():
    id_token = request.cookies.get("token")
    claims = None
    error_message = None
    user_info = None
    user_tweets = []
    result = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)

            query = datastore_client.query(kind="Tweets")
            query.order = ["-date"]

            result = list(query.fetch())
            for tweet in result:
                if tweet['creator'] == user_info['email']:
                    user_tweets.append(tweet)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('profile_page.html', user_data=claims, user_info=user_info, error_message=error_message,
                           user_tweets=user_tweets, add=0)


@app.route('/edit_profile_info')
def edit_profile_info():
    id_token = request.cookies.get("token")
    claims = None
    error_message = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('editProfileInfo.html', user_data=claims, user_info=user_info, error_message=error_message,
                           add=True)


@app.route('/edit_tweet/<int:id>')
def edit_tweet(id):
    id_token = request.cookies.get("token")
    claims = None
    error_message = None
    user_info = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('editTweet.html', user_data=claims, id=id, user_info=user_info, error_message=error_message,
                           add=True)


@app.route('/add_description', methods=['POST'])
def add_description():
    error_message = None
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                          firebase_request_adapter)
    user_tweets = []
    description = request.form['description']

    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    entity.update({
        'description': description
    })
    datastore_client.put(entity)
    user_info = retrieveUserInfo(claims)
    query = datastore_client.query(kind="Tweets")
    query.order = ["-date"]

    result = list(query.fetch())
    for tweet in result:
        if tweet['creator'] == user_info['email']:
            user_tweets.append(tweet)
    return render_template('profile_page.html', user_data=claims, user_info=user_info,
                           user_tweets=user_tweets, error_message=error_message, bool=0)


@app.route('/addTweetPage')
def addTweetPage():
    id_token = request.cookies.get('token')
    error_message = None
    claims = None
    user_info = None

    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
            user_info = retrieveUserInfo(claims)

        except ValueError as exc:
            error_message = str(exc)

    return render_template("add_tweet_page.html", user_data=claims, user_info=user_info)


@app.route('/update_tweet/<int:id>', methods=['POST'])
def update_tweet(id):
    error_message = None
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                          firebase_request_adapter)
    user_tweets = []
    tweet = request.form['tweet']
    print(id)
    entity_key = datastore_client.key('Tweets', id)
    entity = datastore_client.get(entity_key)
    print(entity)
    entity.update({
        'tweet': tweet,

    })
    datastore_client.put(entity)

    user_info = retrieveUserInfo(claims)

    query = datastore_client.query(kind="Tweets")
    query.order = ["-date"]

    result = list(query.fetch())
    for tweet in result:
        if tweet['creator'] == user_info['email']:
            user_tweets.append(tweet)

    return render_template('profile_page.html', user_data=claims, user_info=user_info, error_message=error_message,
                           user_tweets=user_tweets, add=0)


@app.route('/add_tweet', methods=['POST'])
def add_tweet():
    error_message = None
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                          firebase_request_adapter)

    tweet = request.form['tweet']
    id = createTweet(claims, tweet, claims['email'])
    user_info = retrieveUserInfo(claims)
    addTweetToUser(user_info, id)

    user_info = retrieveUserInfo(claims)
    tweets = retrieve_all_tweets()

    return render_template("index.html", user_data=claims, user_info=user_info,
                           tweets=tweets, error_message=error_message, bool=0)


@app.route('/search_users', methods=['POST'])
def searchUsers():
    id_token = request.cookies.get("token")
    error_message = None

    query = datastore_client.query(kind='UserInfo')
    query.add_filter('username', '=', str(request.form['search_u']))

    result = list(query.fetch())

    return render_template('user-list.html', users=result, error_message=error_message, bool=0)


@app.route('/search_context', methods=['POST'])
def searchContext():
    id_token = request.cookies.get("token")
    error_message = None
    tweet_list = []

    print(str(request.form['search_c']))
    tweets = retrieve_all_tweets()
    for tweet in tweets:
        t = tweet['tweet']
        context = str(request.form['search_c']).lower()
        if context in t.lower():
            print("hi")
            tweet_list.append(tweet)
    result = tweet_list
    print(result)
    return render_template('tweet_list.html', tweets=result, error_message=error_message, bool=0)


@app.route('/goto-profile-page/<string:email>')
def gotoprofile_page(email):
    id_token = request.cookies.get("token")
    claims = None
    error_message = None
    user_info = None
    user_tweets = []
    add = 0
    result = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            print(email)
            entity_key = datastore_client.key('UserInfo', email)

            user_info = datastore_client.get(entity_key)
            query = datastore_client.query(kind="Tweets")
            query.order = ["-date"]

            result = list(query.fetch())
            for tweet in result:
                if tweet['creator'] == email:
                    user_tweets.append(tweet)

            followerss = user_info['followers']
            if len(followerss) == 0:
                add = 2
                print("hello")

            for follower in user_info['followers']:
                if claims['email'] == follower:
                    add = 1
                    break
                else:
                    add = 2
        except ValueError as exc:
            error_message = str(exc)
    return render_template('profile_page.html', user_data=claims, user_info=user_info, error_message=error_message,
                           user_tweets=user_tweets, add=add)


@app.route('/follow_user/<string:email>')
def follow_user(email):
    id_token = request.cookies.get("token")
    claims = None
    error_message = None
    user_info = None
    user_tweets = None
    add = 0
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            entityk = datastore_client.key('UserInfo', claims['email'])
            loggedin_user = datastore_client.get(entityk)
            following_list = loggedin_user['followings']
            following_list.append(email)
            loggedin_user.update({
                'followings': following_list
            })
            datastore_client.put(loggedin_user)
            entity_key = datastore_client.key('UserInfo', email)
            user_info = datastore_client.get(entity_key)
            follower_list = user_info['followers']
            follower_list.append(claims['email'])
            user_info.update({
                'followers': follower_list
            })
            datastore_client.put(user_info)
            user_tweets = retrieveTweet(user_info)

            if len(user_info['followers']) == 0:
                add = 2

            for follower in user_info['followers']:
                if claims['email'] == follower:
                    add = 1
                    break
                else:
                    add = 2
        except ValueError as exc:
            error_message = str(exc)
    return render_template('profile_page.html', user_data=claims, user_info=user_info, error_message=error_message,
                           user_tweets=user_tweets, add=add)


@app.route('/unfollow_user/<string:email>')
def unfollow_user(email):
    id_token = request.cookies.get("token")
    claims = None
    error_message = None
    user_info = None
    user_tweets = None
    add = 0
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            print(email)
            entityk = datastore_client.key('UserInfo', claims['email'])
            loggedin_user = datastore_client.get(entityk)
            following_list = loggedin_user['followings']

            following_list.remove(email)
            loggedin_user.update({
                'followings': following_list
            })
            datastore_client.put(loggedin_user)
            entity_key = datastore_client.key('UserInfo', email)
            user_info = datastore_client.get(entity_key)
            follower_list = user_info['followers']
            follower_list.remove(claims['email'])
            user_info.update({
                'followers': follower_list
            })
            datastore_client.put(user_info)
            user_tweets = retrieveTweet(user_info)
            print(user_info['followers'])
            if len(user_info['followers']) == 0:
                add = 2
            print(add)
            for follower in user_info['followers']:
                if claims['email'] == follower:
                    add = 1
                    break
                else:
                    add = 2
                print(add)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('profile_page.html', user_data=claims, user_info=user_info, error_message=error_message,
                           user_tweets=user_tweets, add=add)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
