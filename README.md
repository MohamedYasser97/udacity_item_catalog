# Item Catalog
A simple web app built with Flask that documents items and categories and handles multiple users.


## Code Layout and Flow
The entry point of this project is `app.py`. This file contains all the code that handles the existing endpoints and the logic of each endpoint. `helpers.py` contains some helper methods that are used in `app.py`. All views are stored in the `./templates` directory and a few external CSS styles are in `./static/styles.css`. Both files `db_setup.py` and `db_populate.py` have to run before starting the server in order to set-up and populate the database.

## Execution
First, make sure you have all the required packages installed. You can check those packages in the `requirements.txt` file.
In order to install all of the required packages just execute this command inside the project's directory:

`pip  install  -r  requirements.txt`

Then in order to run this web app, please first set-up and populate the database by executing the following commands in order:

`python db_setup.py`

`python db_populate.py`
  
Now, you can run the server by executing this command:

`python app.py`

You can now use the app in your browser at `http://localhost:8000/`.

## JSON Endpoints
This web app provides the following JSON endpoints.

### `/catalog.json`
This endpoint will return 2 JSON entities, one that has data of all categories and the other has data of all of the items.

---

### `/catalog/category/<category_name>.json`
This endpoint will return data of a specific category and all items that are related to this specific category.

---

### `/catalog/item/<item_name>.json`
This endpoint will return data of a single item along with its owner and parent category.

## FAQ

* __Why can't I edit my category's name?__

  That's because if this category already has items that belong to other users, it would be unethical to change it for them too. However, you can __delete__ your category only if it's empty.
  
* __Why is there a "Add Item" button in the empty category even when I'm logged out?__

  If you try to click on this button it will immediately redirect you to the login page. The button is there to encourage non-users to log-in and contribute.
