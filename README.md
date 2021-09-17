# A simple e-commerce website

1. First step, create virtual environment:

  `python3 -m venv <venv>`

  **<venv>** is virtual environment name.

2. Now activate the virtual environment:

- In *Linux*:

  For bash/zsh

  `source config.sh` or `source ./<venv>/bin/activate`

- In *windows*:

  For cmd: 

  `.\<venv>\Scripts\activate.bat`

  For PowerShell: 

  `.\<venv>\Scripts\Activate.ps1`

For more information: [venv python](https://docs.python.org/es/3.8/library/venv.html)

3. Then install all dependencies doing

  `pip install -r requirements.txt`

  If try to do `flask run` show a error related with dependency **Werkzeug==2.0.1**.

  To solve this you need do:
  [solution](https://stackoverflow.com/questions/61628503/flask-uploads-importerror-cannot-import-name-secure-filename)

  Search `flask_uploads.py` file.

  If you use a virtual environment, look for the file in these possible locations:

  `<venv>/lib/site-packages/flask_uploads.py` or
  `<venv>/lib/python3.X/site-packages/flask_uploads.py`

  Now, in the **flask-uploads.py** file in the imports part, change

  `from werkzeug import secure_filename,FileStorage`

  to

  ```
  from werkzeug.utils import secure_filename
  from werkzeug.datastructures import  FileStorage
  ```
4. Now can start the app doing
  `flask run`

# For login as admin
  test@g.com
  test123456
