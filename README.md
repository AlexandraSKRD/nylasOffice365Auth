#Project setup

##Server setup

* Setup virtualenv
```
python3 -m venv venv
```
* Activate virtualenv
```
source venv/bin/activate
```
* Install dependencies
```
pip install -r requirements.txt
```
* Run the migrations
```
python manage.py migrate
```
* Now you can run django server
```
python manage.py runserver
```



