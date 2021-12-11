import sys
from numpy.lib.function_base import insert, select
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import numpy as np
import pymssql
import datetime
from tabulate import tabulate


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    Takes the command line input 'create_patient <username> <password>'
    and creates a patient in the Patients table. Checks if the username
    already exists in the database and generates a hashed password to 
    store in the database.

    Parameters
    ----------
    tokens : list
        A list of the command line inputs of the form:
            ['create_patient', '<username>', '<password>']
    """
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print(f"Expected 3 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return
    # Extracting inputs
    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if user_name_exists_patients(username):
        print("Username taken, try again!")
        return

    # Generating random salt and hash based off of password and salt.
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    try:
        patient = Patient(username, salt=salt, hash=hash)
        # save to patient information to our database
        try:
            patient.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return
    
        


def user_name_exists_patients(username):
    """
    Checking whether the desired username
    already exists in the Patients table

    Parameters
    ----------
    username : str
        The desired username for the patient

    Returns
    -------
    bool
        Returns True if the username already exists in the 
        Patients table. False if the username is not taken.
    """
    # Creating connection
    cm = ConnectionManager()
    conn = cm.create_connection()

    # Selecting patients where Username matches username given
    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False


def create_caregiver(tokens):
    """
    Takes the command line input 'create_caregiver <username> <password>'
    and creates a caregiver in the Caregivers table. Checks if the username
    already exists in the database and generates a hashed password to 
    store in the database.

    Parameters
    ----------
    tokens : list
        A list of the command line inputs of the form:
            ['create_caregiver', '<username>', '<password>']
    """
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print(f"Expected 3 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)
    # create the caregiver
    try:
        caregiver = Caregiver(username, salt=salt, hash=hash)
        # save to caregiver information to our database
        try:
            caregiver.save_to_db()
        except:
            print("Create failed, Cannot save")
            return
        print(" *** Account created successfully *** ")
    except pymssql.Error:
        print("Create failed")
        return


def username_exists_caregiver(username):
    """
    Checking whether the desired username
    already exists in the Caregivers table

    Parameters
    ----------
    username : str
        The desired username for the caregivers

    Returns
    -------
    bool
        Returns True if the username already exists in the 
        Caregivers table. False if the username is not taken.
    """
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error:
        print("Error occurred when checking username")
        cm.close_connection()
    cm.close_connection()
    return False

def check_login(user, current_patient, current_caregiver):
    """
    Checks if the current user is logged
    in as a patient, caregiver or either.
    Returns a True if they are logged in, 
    else returns False.

    Parameters
    ----------
    user : str
        The type of user to check if logged in.
        Possible values include 'patient', 'caregiver',
        'any'.
    
    Returns
    -------
    status : bool
        returns true if the given user is logged in.
    """
    # global current_caregiver
    # global current_patient
    possible_inputs = ['patient', 'caregiver', 'any']
    if user in possible_inputs:
        if user == 'patient':
            return current_patient is not None
        elif user == 'caregiver':
            return current_caregiver is not None
        elif user == 'any':
            return current_patient is not None or current_caregiver is not None
    else:
        print("User type not defined")
        return

def login_patient(tokens):
    """
    Logs in the current patient using user input 
    credentials

    Parameters
    ----------
    tokens : list
        A list of strings of the user input:
             ['login_patient',  '<username>',  '<password>']
    """
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global current_patient
    if check_login('any', current_patient, current_caregiver):
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print(f"Expected 3 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        try:
            patient = Patient(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if patient is None:
        print("Invalid username or password")
        print("Please try again!")
    else:
        print("Patient logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    """
    Logs in the current caregiver using user input 
    credentials

    Parameters
    ----------
    tokens : list
        A list of strings of the user input:
             ['login_caregiver',  '<username>',  '<password>']
    """
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global current_patient
    if check_login('any', current_patient, current_caregiver):
        print("Already logged-in!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print(f"Expected 3 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        try:
            caregiver = Caregiver(username, password=password).get()
        except:
            print("Get Failed")
            return
    except pymssql.Error:
        print("Error occurred when logging in")

    # check if the login was successful
    if caregiver is None:
        print("Invalid username or password")
        print("Please try again!")
    else:
        print("Caregiver logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    Outputs the username for the caregivers that
    are available for the given date, along with the number of
    available doses left for each vaccine.

    Parameters
    ----------
    tokens : list
        A list of length 2 of the inputs from the command line.
        ['search_caregiver_schedule', '<mm-dd-yyyy>']
    """
    # Check 1: make sure the user is logged in as either a patient
    # or a caregiver
    global current_caregiver
    global current_patient
    if not check_login('any', current_patient, current_caregiver):
        print("Please login first!")
        return
    # Check 2: make sure the length of tokens matches the desired parameter
    #   length
    if len(tokens) != 2:
        print(f"Expected 2 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return

    # Extracting information from token
    date = tokens[1]
    # Check 3: make sure the date string is in the correct format 'mm-dd-yyyy'
    if check_date_format(date) is False:
        return

    # reformating date to 'yyyy-mm-dd'
    re_date = reformat_date(date)
    # Retrieve availability results on 'mm-dd-yyyy'
    # Prints a list of the caregivers
    # create connection
    cm = ConnectionManager()
    conn = cm.create_connection()

    # Get availabilities
    select_caregivers = "SELECT * FROM Availabilities WHERE Time=%s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_caregivers, re_date)
        caregivers = cursor.fetchall()
        if len(caregivers) == 0:
            print(f"No caregivers available on {date}")
            return
        else:
            print(f"Caregivers available on {date}:")
            for row in caregivers:
                print('-', row['Username'])
            print()
    except pymssql.Error:
        print("Error occurred when selecting caregivers")
        cm.close_connection()
    cm.close_connection()
    # Showing the available doses
    show_doses()

def show_availabilities():
    """
    Shows the unique availabilites for appointments.
    You must be logged in as either a patient or a caregiver
    """
    # Check 1: make sure the user is logged in as either a patient
    # or a caregiver
    global current_caregiver
    global current_patient
    if not check_login('any', current_patient, current_caregiver):
        print("Please login first!")
        return

    # Create a connection
    cm = ConnectionManager()
    conn = cm.create_connection()

    # Get unique availabilities (dates)
    select_availabilities = "SELECT DISTINCT Time FROM Availabilities ORDER BY Time ASC"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_availabilities)
        print('Availabilities:')
        for date in cursor.fetchall():
            ref_date = reformat_date(str(date['Time']), inverse=True)
            print(ref_date)
    except pymssql.Error:
        print("Error occurred when selecting availabilities")
        cm.close_connection()
    cm.close_connection()

def reformat_date(date_string, inverse=False):
    """
    Reformats the datestring from 
    'mm-dd-yyyy' to 'yyyy-mm-dd'

    Parameters
    ----------
    date_string : str
        A string containing date information
    inverse : bool
        If inverse is True, it converts from
        'yyyy-mm-dd to mm-dd-yyyy'
    """
    if inverse is False:
        return date_string[6:] + '-' + date_string[0:5]
    else:
        return date_string[5:] + '-' + date_string[0:4]

def check_date_format(date_string):
    """
    Returns False if the format of the date
    string is not in the format 'mm-dd-yyyy'.
    Or if the date is invalid.

    Parameters
    ----------
    date_string : str
        A string containing date information
    """
    date_list = date_string.split('-')
    if len(date_list) != 3:
        print("Invalid date")
        print("Please use format 'mm-dd-yyy'")
        return False
    if len(date_list[0]) != 2 or len(date_list[1]) != 2:
        print("Invalid date")
        print("Please use format 'mm-dd-yyy'")
        return False
    if len(date_list[2]) != 4:
        print("Invalid date")
        print("Please use format 'mm-dd-yyy'")
        return False

    # Testing the values
    for i, val in enumerate(date_list):
        try:
            date_val = int(val)
            if i == 0 and (date_val > 12 or date_val == 0):
                print("Months out of range")
                return False
            if i == 1 and (date_val > 31 or date_val == 0):
                print("Days are out of range")
                return False

        except:
            print("Invalid date format")
            return False
    return True

def show_doses():
    """
    Outputs the current vaccines that are
    available along with the number of available doses.
    """
    # Create connection
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_doses = "SELECT * FROM Vaccines"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_doses)
        # outputing the vaccine name along with doses available
        print("Available Vaccines:")
        headers = ['NAME', 'DOSES']
        cols = ['Name', 'Doses']
        table = []
        for vaccine in cursor:
            row = []
            for colname in cols:
                val = str(vaccine[colname])
                row.append(val)
            table.append(row)
        print(tabulate(table, headers, tablefmt="pretty"))
    except pymssql.Error:
        print("Error occurred when getting current doses")
        cm.close_connection()
        return
    cm.close_connection()

def reserve(tokens):
    """
    Patients can perform this operation to reserve an appointment.
    They are randomly assigned a caregiver for the reservation 
    on that date, the output will be the assigned caregiver and 
    the appointment ID for the reservation.

    Parameters
    ----------
    tokens: list
        list of length 3 of the following format:
        ['reserve', '<mm-dd-yyyy>', '<vaccine name>']
    
    Returns
    -------
    None
    """
    # basic functionality
    # Check 1: make sure the user is logged in as either a patient
    # or a caregiver
    global current_caregiver
    global current_patient
    if not check_login('patient', current_patient, current_caregiver):
        print("Please login as a patient")
        return
    # Check 2: make sure the length of tokens matches the desired parameter
    #   length
    if len(tokens) != 3:
        print(f"Expected 3 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return

    # Extracting information from token
    date = tokens[1]
    vac_name = tokens[2]
    # Check 3: make sure the date string is in the correct format 'mm-dd-yyyy'
    if check_date_format(date) is False:
        return

    # reformating date to 'yyyy-mm-dd'
    re_date = reformat_date(date)

    # create connection
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        # Get Available Caregivers
        try:
            # Check 1: Make sure there is a caregiver available
            select_caregivers = "SELECT Username FROM Availabilities WHERE Time=%s"
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(select_caregivers, re_date)
                available_caregivers = cursor.fetchall() # list of dict
            if len(available_caregivers) == 0:
                print(f"No caregivers available on {date}")
                return
            # Retrieve a random caregiver
            else:
                rand_caregiver = available_caregivers[np.random.randint(0, len(available_caregivers))]['Username']
        except pymssql.Error:
            print("Error occured while checking caregiver availability")
        # Update vaccine doses (removes one dose from vaccine table)
        try:
            remove_dose(vac_name)
        except:
            print("Error in updating vaccine doses")
            return
        # Insert the appointment
        try:
            insert_appointment = "INSERT INTO Appointments VALUES(%d, %s, %s, %s, %s)"
            app_id = get_appointment_id()
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(insert_appointment, (app_id, current_patient.username, rand_caregiver, vac_name, re_date))
        except pymssql.Error:
            print("Error occured when trying to insert appointment")
            conn.rollback()
            cm.close_connection()
            return
        # Remove availability from caregiver
        try:
            remove_availability = "DELETE FROM Availabilities WHERE Username = %s AND Time = %s"
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(remove_availability, (rand_caregiver, re_date))
        except pymssql.Error:
            print("Error occured when updating caregiver availabilities")
            conn.rollback()
            cm.close_connection()
            return
        print("Successfully created appointment!")
        print("Your appointment details:")
        headers = ["Appointment ID", "Date", "Caregiver", "Vaccine"]
        table = [[app_id, date, rand_caregiver, vac_name]]
        print(tabulate(table, headers, tablefmt="pretty"))
    except pymssql.Error:
        print("Error occurred when reserving appointment")
        conn.rollback()
        cm.close_connection()
        return
    conn.commit()
    cm.close_connection()


def get_appointment_id():
    """
    Queries into the Appointments table,
    Finds the max appointment ID and returns
    a new unique appointment ID.
    Generates a unique appointment id:
    gets the list of appoinment ids

    Parameters
    ----------
    None

    Returns
    -------
    int : Unique appointment id
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    # Get max appoinment ID
    select_max_app_id = "SELECT MAX(appointment_id) FROM Appointments"
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(select_max_app_id)
            max_id = cursor.fetchall()[0][0]
            if max_id is None:
                return 1
            else:
                return max_id + 1
        except:
            print("Failed to create appointment id")
    except pymssql.Error:
        print("Error occurred when generating appoinment id")




def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    global current_patient
    if not check_login('caregiver', current_patient, current_caregiver):
        print("Please login as caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        # Check if availability already there
        try:
            cm = ConnectionManager()
            conn = cm.create_connection()
        except:
            print("Failed to create connection")
            return
        try:
            select_availability = 'SELECT * FROM Availabilities WHERE Time=%s AND Username=%s'
            with conn.cursor() as cursor:
                cursor.execute(select_availability, (d, current_caregiver.username))
                rows = cursor.fetchall()
            if len(rows) == 1:
                print("Availability already in system, upload new availability")
                cm.close_connection()
                return
        except:
            print("Failed to check availability")
            cm.close_connection
            return
        try:
            current_caregiver.upload_availability(d)
        except:
            print("Upload Availability Failed")
            return
        print("Availability uploaded!")
    except ValueError:
        print("Please enter a valid date!")
    except pymssql.Error as db_err:
        print("Error occurred when uploading availability")


def cancel(tokens):
    """
    Cancels an appointment given an appointment ID. Both caregivers
    and patients are able to cancel the appointments. This function
    removes the appointment from the Appointments table and updates
    the Caregivers availability schedule.
    
    Parameters
    ----------
    tokens : list
        A list of length 2 of format:
        ['cancel', '<appointment_id>']
    """
    # Check 1: check the token length
    if len(tokens) != 2:
        print(f"Expected 2 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return
    
    # Check 2: Check to make sure appointment id can be made into an integer
    try:
        appointment_id = int(tokens[1])
    except:
        print("Invalid appointment id type")
        print("appointment id must be an integer")
        return
    # Check 3: Make sure the user is logged in as a Caregiver or Patient
    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    elif current_caregiver is not None:
        condition = f"c_username='{current_caregiver.username}'"
    else:
        condition = f"p_username='{current_patient.username}'"
    
    # Get the caregiver's username
    cm = ConnectionManager()
    conn = cm.create_connection()
    try:
        try:
            select_caregiver = f"""SELECT c_username, Time, vac_name 
                                    FROM Appointments 
                                WHERE appointment_id=%s AND
                                        {condition}"""
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(select_caregiver, appointment_id)
                app = cursor.fetchone()
                caregiver = app['c_username']
                date = app['Time']
                vaccine = app['vac_name']
        except:
            print("Failed to retrieve appointment")
            return
        if caregiver is None:
            print("Appointment does not exist")
            return
        else:
            # Delete the appointment
            delete_appointment = "DELETE FROM Appointments WHERE appointment_id=%s"
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute(delete_appointment, appointment_id)
            # Add back availability
            try:
                try:
                    insert_availability = """INSERT INTO Availabilities VALUES(%s, %s)"""
                    with conn.cursor() as cursor:
                        cursor.execute(insert_availability, (date.strftime("%Y-%m-%d"), caregiver))
                except:
                    print("Update Availability Failed")
                    conn.rollback()
                    cm.close_connection()
                    return
            except pymssql.Error as db_err:
                print("Error occurred when uploading availability")
            # Update vaccine doses
            try:
                add_doses(['add_doses', vaccine, 1], override=True)
            except:
                print("Failed to update doses!")
                conn.rollback()
                cm.close_connection()
                return
    except pymssql.Error:
        print("Error while trying to retrieve appointment")
        cm.close_connection()
        return
    print("You have successfully cancelled your appointment.")
    # Cancel the appointment
    conn.commit()
    cm.close_connection()


def remove_dose(vaccine_name):
    """
    Removes a single dose from the specified vaccine
    in the vaccines table.

    Parameters
    ----------
    vaccine_name : str
        A string that specifies the name of the vaccine
        in the Vaccines Table
    """
    try:
        try:
            vaccine = Vaccine(vaccine_name, 0).get()
            if vaccine is None:
                print("Vaccine", vaccine_name, "does not exist")
                show_doses()
                return
        except:
            print("Failed to get Vaccine")
            return
    except pymssql.Error:
        print("Error occured when removing dose")
        return
    # Remove dose from Vaccine
    try:
        try:
            vaccine.decrease_available_doses(1)
        except:
            print("Failed to decrease available doses")
            return
    except pymssql.Error:
        print("Error occured when updating Vaccine doses")
        return

def add_doses(tokens, override=False):
    """
    An operation that can be used only by Caregivers. It allows
    them to add doses to the Vaccines table. If the vaccine does
    not currently exist a new vaccine is added with the provided
    number of doses. If that vaccine does exist the number of doses
    is incremented by the number specified by the user

    Parameters
    ----------
    tokens : list
        A list of strings of the format:
        ['add_doses', 'vaccine', <number>] 
            - vaccine: Name of the vaccine
            - number: number of vaccines
    override : bool, optional
        If override is true, the function does not care
        if the current logged in user is a caregiver. This is so
        patients can cancel their appointments and effectively 'add back'
        a vaccine dose for availability, by default False
    """
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    if override is False:
        global current_caregiver
        global current_patient
        if not check_login('caregiver', current_patient, current_caregiver):
            print("Please login as caregiver first!")
            return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print(f"Expected 3 inputs, received {len(tokens)} inputs")
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    try:
        doses = int(tokens[2])
        if doses < 0:
            print("Number of doses must be a positive integer")
            print("Please try again!")
            return
    except ValueError:
        print("Number of doses must be a positive integer!")
        print("Please try again!")
        return
    vaccine = None
    try:
        try:
            vaccine = Vaccine(vaccine_name, doses).get()
        except:
            print("Failed to get Vaccine!")
            return
    except pymssql.Error:
        print("Error occurred when adding doses")

    # check 3: if getter returns null, it means that we 
    # need to create the vaccine and insert it into the Vaccines table
    if vaccine is None:
        try:
            vaccine = Vaccine(vaccine_name, doses)
            try:
                vaccine.save_to_db()
            except:
                print("Failed To Save")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            try:
                vaccine.increase_available_doses(doses)
            except:
                print("Failed to increase available doses!")
                return
        except pymssql.Error:
            print("Error occurred when adding doses")
    if not override:
        print("Doses updated!")


def show_appointments():
    """
    Outputs the scheduled appointments for the given user
    (Patient or Caregiver) as a table that includes the 
    appointment id, Patient/Caregiver name, Vaccine, and date
    """
    global current_patient
    global current_caregiver

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        if current_caregiver is not None:
            try:
                # Retrieve caregiver appointments
                select_appointments = "SELECT * FROM Appointments WHERE c_username=%s"
                cursor.execute(select_appointments, current_caregiver.username)
                name = 'p_username'
            except:
                print("Failed to retrieve caregiver appointments")
        elif current_patient is not None:
            try:
                select_appointments = "SELECT * FROM Appointments WHERE p_username=%s"
                cursor.execute(select_appointments, current_patient.username)
                name = 'c_username'
            except:
                print("Failed to retrieve patient appointments")
        else:
            print("Not currently logged in")
            print("Please login first!")
            return
        # Printing the output
        if name == 'p_username':
            person = 'PATIENT        '
        elif name == 'c_username':
            person = 'CAREGIVER      '
        print("Appointments:")
        headers = ["APPOINTMENT ID", person, "VACCINE", "DATE"]
        # generating rows
        cols = ['appointment_id', name, 'vac_name', 'Time']
        table = []
        for appointment in cursor.fetchall():
            row = []
            for colname in cols:
                val = str(appointment[colname])
                row.append(val)
            table.append(row)
        print(tabulate(table, headers, tablefmt="pretty"))

    except pymssql.Error:
        print("Error in retrieving appointments!")

def logout(tokens):
    """
    Logs out the current user from the database.

    Parameters
    ----------
    tokens : list
        A list of the user input of the form
        ['logout']
    """
    # Check 1: check the length of the input
    if len(tokens) != 1:
        print("Invalid token length")
        print("Please try again!")
        return
    
    global current_caregiver
    global current_patient

    if current_caregiver is not None:
        print(f"Logging out caregiver {current_caregiver.username}")
        current_caregiver = None
    elif current_patient is not None:
        print(f"Logging out patient {current_patient.username}")
        current_patient = None
    else:
        print("Not currently logged in")
        return
    print("Successfully logged out")
    return


def start():
    stop = False
    while not stop:
        if current_caregiver is None and current_patient is None:
            print()
            print("+----------------------------------------+")
            print("|   PLEASE LOGIN OR CREATE AN ACCOUNT!   |")
            print("+----------------------------------------+")
            print()
            print(" *** Available Commands *** ")
            print("> create_patient <username> <password>")
            print("> create_caregiver <username> <password>")
            print("> login_patient <username> <password>")
            print("> login_caregiver <username> <password>")
            print("> Quit")
            print()
        elif current_caregiver is not None:
            print()
            print("+----------------------------------------+")
            print("|           WELCOME CAREGIVER!           |")
            print("+----------------------------------------+")
            print()
            print(" *** Available Commands *** ")
            print("Vaccine Management:")
            print("-------------------")
            print("> show_doses")
            print("> add_doses <vaccine> <number>")
            print()
            print("Scheduler:")
            print("----------")
            print("> show_appointments")  
            print("> upload_availability <date>")
            print("> cancel <appointment_id>") 
            print("> show_availabilities")
            print()
            print("Logout:")
            print("-------")
            print("> logout")
            print("> Quit")
            print()
        else:
            print()
            print("+----------------------------------------+")
            print("|            WELCOME PATIENT!            |")
            print("+----------------------------------------+")
            print()
            print(" *** Available Commands *** ")
            print("Schedule an Appointment:")
            print("------------------------")
            print("> show_availabilities")
            print("> show_doses")
            print("> search_caregiver_schedule <date>")
            print("> reserve <date> <vaccine>")
            print()
            print("Manage Existing Appointments:")
            print("-----------------------------")
            print("> show_appointments")
            print("> cancel <appointment_id>")
            print()
            print("Logout:")
            print("-------")
            print("> logout")
            print("> Quit")
            print()

        response = ""
        print("> Enter: ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Type in a valid argument")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Try Again")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_doses":
            show_doses()
        elif operation == "show_availabilities":
            show_availabilities()
        elif operation == "show_appointments":
            show_appointments()
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Thank you for using the scheduler, Goodbye!")
            stop = True
        else:
            print("Invalid Argument")


if __name__ == "__main__":
    # start command line
    print()
    print("+---------------------------------------------------------------------+")
    print("| Welcome to the COVID-19 Vaccine Reservation Scheduling Application! |")
    print("+---------------------------------------------------------------------+")

    start()
