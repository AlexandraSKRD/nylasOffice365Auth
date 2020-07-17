# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from tutorial.auth_helper import get_sign_in_url, get_token_from_code, store_token, store_user, remove_user_and_token, \
    get_token
from tutorial.graph_helper import get_user
import dateutil.parser
import yaml
from nylas import APIClient
import requests

stream = open('oauth_settings.yml', 'r')
settings = yaml.load(stream, yaml.SafeLoader)


# <HomeViewSnippet>
def home(request):
    context = initialize_context(request)

    return render(request, 'tutorial/home.html', context)


# </HomeViewSnippet>

# <InitializeContextSnippet>
def initialize_context(request):
    context = {}

    # Check for any errors in the session
    error = request.session.pop('flash_error', None)

    if error != None:
        context['errors'] = []
        context['errors'].append(error)

    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context


# </InitializeContextSnippet>

# <SignInViewSnippet>
def sign_in(request):
    # Get the sign-in URL
    sign_in_url, state = get_sign_in_url()
    # Save the expected state so we can validate in the callback
    request.session['auth_state'] = state
    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(sign_in_url)


# </SignInViewSnippet>

# <SignOutViewSnippet>
def sign_out(request):
    # Clear out the user and token
    remove_user_and_token(request)

    return HttpResponseRedirect(reverse('home'))


# </SignOutViewSnippet>

# <CallbackViewSnippet>
def callback(request):
    # Get the state saved in session
    expected_state = request.session.pop('auth_state', '')
    # Make the token request

    token = get_token_from_code(request.get_full_path(), expected_state)
    # Get the user's profile
    user = get_user(token)
    # #Get nylas code
    api_client = APIClient(app_id="57j65z6aezdxuocajwwegvkyx", app_secret="du2z08iomhm6remzvzyhk8bz9")
    response_body = {
        "client_id": api_client.app_id,
        "name": user['givenName'],
        "email_address": user['mail'],
        "provider": "office365",
        "settings": {
            "microsoft_client_id": settings['app_id'],
            "microsoft_client_secret": settings['app_secret'],
            "microsoft_refresh_token": token['refresh_token'],
            "redirect_uri": settings['redirect'],
        },
        "scopes": "email.read_only,calendar"
    }
    nylas_authorize_resp = requests.post(
        "https://api.nylas.com/connect/authorize", json=response_body
    )

    nylas_code = nylas_authorize_resp.json()["code"]

    # Get nylas access_token

    nylas_token_data = {
        "client_id": api_client.app_id,
        "client_secret": api_client.app_secret,
        "code": nylas_code,
    }

    nylas_token_resp = requests.post(
        "https://api.nylas.com/connect/token", json=nylas_token_data
    )

    if not nylas_token_resp.ok:
        message = nylas_token_resp.json()["message"]
        return requests.Response('Bad Request')

    nylas_access_token = nylas_token_resp.json()["access_token"]

    print(nylas_access_token)

    # Save token and user
    store_token(request, token)
    store_user(request, user)

    return HttpResponseRedirect(reverse('home'))


# </CallbackViewSnippet>


