# item-catalog
A general-use application for displaying lists of items by category
and the item descriptions.

### Getting Started

Follow these steps to get started:

```
	> git clone https://github.com/dannytpeck/item-catalog
	> cd item-catalog
  > pip install flask sqlalchemy oauth2client
	> python application.py
```

### Changing the port

By default, the application runs on port 8000. That can be changed
at the bottom of application.py

```
    app.run(host='0.0.0.0', port=8000)
```

### Using Google Oauth

Logging into the application to make changes to the Categories and
Items requires a Google account. To get this working properly, you
will need to [set up credentials](https://console.developers.google.com/apis/)

Make sure to download the supplied client secrets JSON file into
the /item-catalog (or whatever directory you use) and rename the
file to "client_secrets.json"
