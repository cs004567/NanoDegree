
# Sports Catalog Web Site

This project creates a flask based catalog web site of sports items.  The site allows for browsing of items and viewing their details grouped under catagories.  You can authenticate via Google Sign In and manage your own items.  You can add items to a category and edit or delete items you have added.

## Usage

To launch the server use the folloing command and access the site via http://localhost:5000/

/usr/bin/python project.py

## Requirements

1. Vagrant - Download from [here](https://www.vagrantup.com)
2. VirtualBox - Download from [here](https://www.virtualbox.org)
3. VM Configuration from Udacity available from github [here](https://github.com/udacity/fullstack-nanodegree-vm)

**Google Sign In**

In order to utilize _Google Sign In_ you will need to configure the application within the [Google Sign In](https://developers.google.com/identity/) dashboard and include the client_secrets.json file in the folder with project.py.

http://localhost:5000/login and http://localhost:5000/gconnect will need to be included as redirect URIs.

## Database Information

The database consists of three tables:
1. user: Holds local user informtion.
2. category: Hold a list of the _categories_ available for items to be assigned to.
3. item: Holds all the individual _items_.  Each row also holds the reference to the item's category and the user which added the item to the database.

The script sampledbdata.py is included which will populate the database with initial categories and a few items.

## API Access

Pages with JSON API data exports will have a **Show Data** link available at the bottom of the page.

## CSS

Some elements of the CSS for this site are from [w3schools.com](https://www.w3schools.com/w3css/w3css_templates.asp).  Per the site they are free to modify, save, share, and use.
