## Virtual Envirnoment and requirements

- Python version 3.8
- Mysql version 8.0

```
Create environment inside project directory:

creating virtual environment : python -m venv env
activating virtual environment : source env/bin/activate

```

Set enivronment variables in your system and give the appropriate values as required. For more help, please refer vars.example.env. All necessary environment variables are mentioned here.


### Running without Docker

```
# Set environment variables according to vars.example.env on your local system

# Install dependencies, run the below command inside api directory :

pip install -r requirements.txt

# Run the below command inside src directory to create the tables inside the database using alembic migrations :

alembic -c migrations/alembic.ini upgrade head

# Run the below command inside api directory to up the FastAPI Service using Hypercorn:

hypercorn src/main:app --bind 0.0.0.0:{port} --reload

# use {base_path}/docs to reach OpenAPI interface

#command for creating new migration if needed, run the below command inside src directory :

alembic -c migrations/alembic.ini revision --autogenerate -m "<message>"

```

### Running with Docker
```
# Run inside api directory:

# Build Docker Image and run
docker-compose -f docker-compose.yml up --build 

# Run Detached in Background
docker-compose -f docker-compose.yml up --build -d

# Run mysql server 
docker-compose -f docker-mysql.yml up --build 

# Stops containers and removes containers, networks, volumes, and images
docker-compose down

# To up containers
docker-compose up

# To stop containers
docker-compose stop

- Notes

# while running through docker, make sure to put all necessary environment variables with their values inside vars.env

# Api can be reached via {base_path}/approvals

# this assumes /approvals in nginx config (main server) is mapped to port 8080 of approvals server.

# docker container should be running in the same network as main server

```

### To Test the API's

Run the below command inside api directory :

pytest -v

- Notes

for more info, run 'pytest --help'

Please make sure to update the correct test data inside test_data.py inside tests directory.

### Code Linting

Run the below command explicitly in terminal :

black <filename>/<path>

- Notes

Please make sure 'Black' is installed. For more info, please refer 'https://pypi.org/project/black/'


### Expected Environment Variables
```
TIER -> local, dev or production. Enables picking the right config
```

### Approval Notification Job Script

run the below command inside src directory to execute the script

python -m script.approval_notification_job

- Notes

The Script will fetch all the record from the ApprovalNotificationJob table and send them email/notification as per the type and once it done then delete the entry from the table.

### Non-GUI mode for Load Testing using JMeter

- install Apache Jmeter https://jmeter.apache.org/download_jmeter.cgi

- go to bin directory of Apache JMeter

- run the below command to perform the test, but before that you need to convert your Postman collection into .jmx format

./jmeter -n -t <location-of-jmeter-script> -l <location-of-result-file> -e -o <location-of-output-folder>

ex: ./jmeter -n -t /home/shivam/Downloads/apache-jmeter-5.5/bin/LoadTest/list_approval.jmx -l /home/shivam/Downloads/apache-jmeter-5.5/bin/LoadTest/load_test_result.csv -e -o /home/shivam/Downloads/apache-jmeter-5.5/bin/LoadTest/HtmlReport

-  For viewing the result, go to specified location folder of results. For HtmlReport, open the index.html file that has been created on your browser

for more info, please refer :

https://www.numpyninja.com/post/run-jmeter-and-generate-html-dashboard-report-from-command-line-non-gui-mode

### GUI Mode

- go to bin directory of Apache JMeter

- run the below command to open JMeter GUI

./jmeter 

* Create Test Plan
* Create Thread Group (Number of Threads/ Ramp-up period/ Loop Count)
    - right click on Test Plan -> Add -> Threads (Users) -> Thread Group
* Add API to Thread Group
    - right click on Thread Group -> Add -> Sampler -> HTTP Request 
* Add Listener to Thread Group for view result
    - right click on Thread Group -> Add -> Listener -> View Results Tree 
    - right click on Thread Group -> Add -> Listener -> Summary Report 
* Add Auth token inside API
    - right click on API -> Add -> Config Element -> HTTP Header Manager

