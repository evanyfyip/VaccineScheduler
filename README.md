# Python Application for Vaccine Scheduler
## Introduction
Vaccine Scheduler is a Command Line based scheduler program that allows users to interact with a Microsoft Azure database via command line commands. Users can create accounts as Patients or Caregivers and login to access the database.

## Installing Directly from Github
1. Download VaccineScheduler. Click the green button at the top of this page that says "Code" and select "Download ZIP". Unzip the file into the desired working directory
2. Navigate to the working directory
3. Install the base dependencies. Run pip install -r requirements.txt.

## Setting up the database
To set up your Microsoft Azure database you can follow the following instructions:
- [Azure Setup Guide](https://docs.google.com/document/d/1tFPsFv6-7nSk49zPl6c_G4dFS6oMBxhnwyUMj9T2nO0/edit)
Creating the tables:
1. Navigate to src/main/resources/create.sql
2. Run the create.sql file on the azure database to create the tables

## Connecting to the database
Setup the environment variables:
- Use your credentials from azure

In your terminal run the following commands: (replace generic terms with your credentials)
```
export Server=example.database.windows.net
export DBName=exampledatabase
export UserID=Username@example.database.windows.net
export Password=password123
```
## Running the Vaccine Scheduler
To run the vaccine scheduler:
1. Navigate to src/main/scheduler
2. run `python Scheduler.py`
3. Follow the prompts to interact with the database
