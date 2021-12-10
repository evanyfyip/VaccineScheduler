import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Patient:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        """
        Get the patient with that matches the Username and
        Salt and Hash
        
        Parameters
        ----------
        self : Patient object
            fields:
                - username
                - password
                - salt
                - hash
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_patient_details = "SELECT Salt, Hash FROM Patients WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash'] # stored hash
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    return self
        except pymssql.Error:
            print("Error occurred when getting Patients")
            cm.close_connection()

        cm.close_connection()
        return None

    def get_username(self):
        """
        Returns the username of the patient
        object.

        Returns
        -------
        str
            The patient username
        """
        return self.username

    def get_salt(self):
        """
        Returns the salt of the patient
        object.

        Returns
        -------
        str
            The patient salt
        """
        return self.salt

    def get_hash(self):
        """
        Returns the hash of the patient
        object.

        Returns
        -------
        str
            The patient hash
        """
        return self.hash

    def save_to_db(self):
        """
        Saves the current patient object into
        the Patients table in the database.
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_patients = "INSERT INTO Patients VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_patients, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error as db_err:
            print("Error occurred when inserting Patients")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            cm.close_connection()
        cm.close_connection()

    # # Insert availability with parameter date d
    # def upload_availability(self, d):
    #     """
    #     Uploads the availability of the Patient
    #     into the Availabilities Table in the database.

    #     Parameters
    #     ----------
    #     d : str
    #         Date time string of the format 'mm-dd-yyyy'.
    #     """
    #     cm = ConnectionManager()
    #     conn = cm.create_connection()
    #     cursor = conn.cursor()

    #     add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
    #     try:
    #         cursor.execute(add_availability, (d, self.username))
    #         # you must call commit() to persist your data if you don't set autocommit to True
    #         conn.commit()
    #     except pymssql.Error:
    #         print("Error occurred when updating patient availability")
    #         cm.close_connection()
    #     cm.close_connection()
