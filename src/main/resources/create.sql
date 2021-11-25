-- Creating User table
CREATE TABLE Users (
    Username varchar(255),
    Name varchar(50),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

-- Creating Caregivers table
CREATE TABLE Caregivers (
    Username varchar(255) REFERENCES Users,
    PRIMARY KEY (Username)
);

-- Creating Patients table
CREATE TABLE Patients (
    Username varchar(255) REFERENCES Users,
    PRIMARY KEY (Username)
);

-- Creating Current availabilities table
CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

-- Creating Vaccines table (what is in stock)
CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

-- Creating Appointments table
CREATE TABLE Appointments (
    appointment_id INT,
    p_username varchar(255) REFERENCES Patients(Username),
    c_username varchar(255) REFERENCES Caregivers(Username),
    vac_name varchar(255) REFERENCES Vaccines(Name),
    Time date
);