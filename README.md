# Item Catalog
A simple web app built with Flask that documents items and categories and handles multiple users.


## Code Layout and Flow
The entry point of this project is `app.py`. This file contains all the code that handles the existing endpoints and the logic of each endpoint. `helpers.py` contains some helper methods that are used in `app.py`. All views are stored in the `./templates` directory and a few external CSS styles are in `./static/styles.css`. Both files `db_setup.py` and `db_populate.py` have to run before starting the server in order to set-up and populate the database.

## Execution
In order to run this web app, please first set-up and populate the database by executing the following commands in order:

  1) `python db_setup.py`
  2) `python db_populate.py`
  
Now, you can run the server by executing this command:

`python app.py`

You can now use the app in your browser at `http://localhost:8000/`.

## JSON Endpoints
This web app provides two types of JSON endpoints.

`http://localhost:8000/catalog.json` will return 2 JSON entities, one that has data on all categories and the other has data on all of the items.

`http://localhost:8000/catalog/category/<category_name>.json` will return data on a specific category and all items that are related to this specific category.


## FAQ

* __Why can't I edit my category's name?__

  That's because if this category already has items that belong to other users, it would be unethical to change it for them too. However, you can __delete__ your category only if it's empty.
  
* __Why is there a "Add Item" button in the empty category even when I'm logged out?__

  If you try to click on this button it will immediately redirect you to the login page. The button is there to encourage non-users to log-in and contribute.
