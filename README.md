# A simple e-commerce website

1. First step, activate virtual enviroment doing:

In Linux:
`source config.sh`

In windows:
*TODO*

2. Then install all dependencies doing

`pip install -r requirements.txt`
Exist a problem with dependency **Werkzeug==2.0.1**.
To solve this you need do:
[solve](https://stackoverflow.com/questions/61628503/flask-uploads-importerror-cannot-import-name-secure-filename)

In `flask_uploads.py` imports

Change

`from werkzeug import secure_filename,FileStorage`

to

```
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
```

If use virtual an environment search the file in this possible options:
`venv/lib/site-packages/flask_uploads.py`
`venv/lib/python3.X/site-packages/flask_uploads.py`

3. Now we can start the app
`flask run`

# For login as admin
test@g.com
test12345
