# PWP SPRING 2020
# PROJECT NAME
# Group information
* Student 1. Xin Shu, mr_comfort@163.com
* Student 2. Mirko Kopsa, mirko.kopsa@gmail.com
* Student 3. Sihan Zhu, sihanzhu22@gmail.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Dependencies

Go to the application folder and execute the following command:

```
pip install -r requirements.txt
```

requirements.txt:
```
aniso8601==6.0.0
appnope==0.1.0
attrs==19.1.0
backcall==0.1.0
certifi==2019.3.9
chardet==3.0.4
Click==7.0
colorama==0.4.1
coverage==5.0.3
decorator==4.4.0
Flask==1.0.2
Flask-RESTful==0.3.7
Flask-SQLAlchemy==2.3.2
idna==2.8
importlib-metadata==1.5.0
ipython==7.4.0
ipython-genutils==0.2.0
itsdangerous==1.1.0
jedi==0.13.3
Jinja2==2.10
jsonschema==3.0.1
MarkupSafe==1.1.1
more-itertools==8.2.0
packaging==20.1
parso==0.3.4
pexpect==4.8.0
pickleshare==0.7.5
pluggy==0.13.1
prompt-toolkit==2.0.9
ptyprocess==0.6.0
py==1.8.1
Pygments==2.3.1
pyparsing==2.4.6
pyrsistent==0.14.11
pytest==5.3.5
pytest-cov==2.8.1
pytz==2018.9
requests==2.21.0
six==1.12.0
SQLAlchemy==1.3.1
svgwrite==1.3.1
traitlets==4.3.2
urllib3==1.24.1
wcwidth==0.1.7
Werkzeug==0.15.1
zipp==3.0.0
```

## Create and poplulate the database, and Running the API
The app of databse and API is created inside __init.py__ of the eventhub folder.
For Windows, run this one level above the eventhub folder.
```
set FLASK_APP=eventhub
set FLASK_ENV=develpment
flask run
```
And the database is up and running, as well as the API. You can easily add data e.g. using TablePlus.

## Testing the database
The db_test.py in the "test" folder can be used for testing
```
pytest db_test.py
```

### Sending requests

You can import the Insomnia.json file to [Insomnia](https://insomnia.rest) to send requests.

## Testing the API
The test for the API is also in the test folder. 
The command to test the API:
```
pytest resource_test.py
```
