# Item Catalog
An item catalog web service.
## Features:
* Provides list of categories
* Displays recently added items
* Provides a list of items within a variety of categories.
* User registration and authentication system.
* Registered users have the ability to post, edit and delete their own items.
* Json api for categories, items.

## Requirements:
* Python 2.7.11
* SQLite 3.9.2
* Flask 0.9
* SQLAlchemy 1.0.12
* Google+ Client Secrets(client_secrets.json)

## Installation:
* Download the repository
* Setup Google Plus authentication
    * Go to https://console.developers.google.com/project and login with Google.
    * Create a new project
    * Name the project
    * Select "API's and Auth-> Credentials-> Create a new OAuth client ID" from the project menu
    * Select Web Application
    * On the consent screen, type in a product name and save.
    * In Authorized javascript origins add: http://0.0.0.0:5000 http://localhost:5000
    * Click create client ID
    * Click download JSON and save it into the root director of this project.
    * Rename the JSON file "client_secret.json"
    * In main.html replace the "data-clientid="" with your Client ID from the web applciation.
* Setup database
`python database_setup.py`
* Run the project
 `python project.py`
* Navigate to http://localhost:5000
