# My Course Rocks

> Track your favourite course at ASU and get notified if a seat becomes available in it.

## NOTE: This is an alpha version. Expect lot of bugs.
## Only tested for some CSE courses

## Development
Python 3.6+ required. Clone this repo and follow these steps:
```sh
pipenv install -r requirements.txt
python app.py

# get classes and seats for a course:
curl http://127.0.0.1:5000/courseseats/CSE/355
# get seats of a particular class
curl http://127.0.0.1:5000/classseats/83239
# get description of a particular class
curl http://127.0.0.1:5000/class/83239
```