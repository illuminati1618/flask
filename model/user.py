""" database dependencies to support sqliteDB examples """
from flask import current_app
from flask_login import UserMixin
from datetime import date
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

from __init__ import app, db
from model.github import GitHubUser
from model.kasm import KasmUser
from model.stocks import StockUser


""" Helper Functions """

def default_year():
    """Returns the default year for user enrollment based on the current month."""
    current_month = date.today().month
    current_year = date.today().year
    # If current month is between August (8) and December (12), the enrollment year is next year.
    if 7 <= current_month <= 12:
        current_year = current_year + 1
    return current_year 

""" Database Models """

''' Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along '''

class UserSection(db.Model):
    """ 
    UserSection Model

    A many-to-many relationship between the 'users' and 'sections' tables.

    Attributes:
        user_id (Column): An integer representing the user's unique identifier, a foreign key that references the 'users' table.
        section_id (Column): An integer representing the section's unique identifier, a foreign key that references the 'sections' table.
        year (Column): An integer representing the year the user enrolled with the section. Defaults to the current year.
    """
    __tablename__ = 'user_sections'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), primary_key=True)
    year = db.Column(db.Integer)

    # Define relationships with User and Section models 
    user = db.relationship("User", backref=db.backref("user_sections_rel", cascade="all, delete-orphan"))
    # Overlaps setting avoids cicular dependencies with Section class.
    section = db.relationship("Section", backref=db.backref("section_users_rel", cascade="all, delete-orphan"), overlaps="users")
    
    def __init__(self, user, section):
        self.user = user
        self.section = section
        self.year = default_year()


class Section(db.Model):
    """
    Section Model
    
    The Section class represents a section within the application, such as a class, department or group.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the section.
        _name (db.Column): A string representing the name of the section. It is not unique and cannot be null.
        _abbreviation (db.Column): A unique string representing the abbreviation of the section's name. It cannot be null.
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _abbreviation = db.Column(db.String(255), unique=True, nullable=False)
  
    # Define many-to-many relationship with User model through UserSection table
    # Overlaps setting avoids cicular dependencies with UserSection class
    users = db.relationship('User', secondary=UserSection.__table__, lazy='subquery',
                            backref=db.backref('section_users_rel', lazy=True, viewonly=True), overlaps="section_users_rel,user_sections_rel,user")    
    
    # Constructor
    def __init__(self, name, abbreviation):
        self._name = name 
        self._abbreviation = abbreviation
        
    @property
    def abbreviation(self):
        return self._abbreviation

    # String representation of the Classes object
    def __repr__(self):
        return f"Class(_id={self.id}, name={self._name}, abbreviation={self._abbreviation})"

    # CRUD create
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read
    def read(self):
        return {
            "id": self.id,
            "name": self._name,
            "abbreviation": self._abbreviation
        }
        
    # CRUD delete: remove self
    # None
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return None


class User(db.Model, UserMixin):
    """
    User Model

    This class represents the User model, which is used to manage actions in the 'users' table of the database. It is an
    implementation of Object Relational Mapping (ORM) using SQLAlchemy, allowing for easy interaction with the database
    using Python code. The User model includes various fields and methods to support user management, authentication,
    and profile management functionalities.

    Attributes:
        __tablename__ (str): Specifies the name of the table in the database.
        id (Column): The primary key, an integer representing the unique identifier for the user.
        _name (Column): A string representing the user's name. It is not unique and cannot be null.
        _uid (Column): A unique string identifier for the user, cannot be null.
        _email (Column): A string representing the user's email address. It is not unique and cannot be null.
        _sid (Column): A string representing the user's student ID. It is not unique and can be null.
        _password (Column): A string representing the hashed password of the user. It is not unique and cannot be null.
        _role (Column): A string representing the user's role within the application. Defaults to "User".
        _pfp (Column): A string representing the path to the user's profile picture. It can be null.
        kasm_server_needed (Column): A boolean indicating whether the user requires a Kasm server.
        sections (Relationship): A many-to-many relationship between users and sections, allowing users to be associated with multiple sections.
        _grade_data (Column): A JSON object representing the user's grade data.
        _ap_exam (Column): A JSON object representing the user's AP exam data.
        _school (Column): A string representing the user's school, defaults to "Unknown".
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _email = db.Column(db.String(255), unique=False, nullable=False)
    _sid = db.Column(db.String(255), unique=False, nullable=True)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _role = db.Column(db.String(20), default="User", nullable=False)
    _pfp = db.Column(db.String(255), unique=False, nullable=True)
    kasm_server_needed = db.Column(db.Boolean, default=False)
    _grade_data = db.Column(db.JSON, unique=False, nullable=True)
    _ap_exam = db.Column(db.JSON, unique=False, nullable=True)
    _school = db.Column(db.String(255), default="Unknown", nullable=True)

    # Define many-to-many relationship with Section model through UserSection table 
    # Overlaps setting avoids cicular dependencies with UserSection class
    sections = db.relationship('Section', secondary=UserSection.__table__, lazy='subquery',
                               backref=db.backref('user_sections_rel', lazy=True, viewonly=True), overlaps="user_sections_rel,section,section_users_rel,user,users")
    
    # Define one-to-one relationship with StockUser model
    stock_user = db.relationship("StockUser", backref=db.backref("users", cascade="all"), lazy=True, uselist=False)

    def __init__(self, name, uid, password=app.config["DEFAULT_PASSWORD"], kasm_server_needed=False, role="User", pfp='', grade_data=None, ap_exam=None, school="Unknown", sid=None):
        self._name = name
        self._uid = uid
        self._email = "?"
        self._sid = sid
        self.set_password(password)
        self.kasm_server_needed = kasm_server_needed
        self._role = role
        self._pfp = pfp
        self._grade_data = grade_data if grade_data else {}
        self._ap_exam = ap_exam if ap_exam else {}
        self._school = school

    # UserMixin/Flask-Login requires a get_id method to return the id as a string
    def get_id(self):
        return str(self.id)

    # UserMixin/Flask-Login requires is_authenticated to be defined
    @property
    def is_authenticated(self):
        return True

    # UserMixin/Flask-Login requires is_active to be defined
    @property
    def is_active(self):
        return True

    # UserMixin/Flask-Login requires is_anonymous to be defined
    @property
    def is_anonymous(self):
        return False
    
    # validate uid is a unique GitHub username
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        if email is None or email == "":
            self._email = "?"
        else:
            self._email = email
        
    def set_email(self):
        """Set the email of the user based on the UID, the GitHub username."""
        data, status = GitHubUser().get(self._uid)
        if status == 200:
            self.email = data.get("email", "?")
            pass
        else:
            self.email = "?"

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name

    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name

    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid

    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid

    # Student ID getter method
    @property
    def sid(self):
        return self._sid

    # Student ID setter function
    @sid.setter
    def sid(self, sid):
        self._sid = sid

    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid

    @property
    def password(self):
        return self._password[0:10] + "..."  # because of security only show 1st characters

    # set password, this is conventional setter with business logic
    def set_password(self, password):
        """Set password: hash if not already hashed, else set directly."""
        if password and password.startswith("pbkdf2:sha256:"):
            # Already hashed, set directly
            self._password = password
        else:
            # Not hashed, hash it
            self._password = generate_password_hash(password, "pbkdf2:sha256", salt_length=10)            

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result

    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    def is_admin(self):
        return self._role == "Admin"

    def is_teacher(self):
        return self._role == "Teacher"
    
    # getter method for profile picture
    @property
    def pfp(self):
        return self._pfp

    # setter function for profile picture
    @pfp.setter
    def pfp(self, pfp):
        self._pfp = pfp

    @property
    def grade_data(self):
        """Gets the user's grade data."""
        if self._grade_data is None:
            return {}
        return self._grade_data

    @grade_data.setter
    def grade_data(self, grade_data):
        """Sets the user's grade data."""
        self._grade_data = grade_data if grade_data is not None else {}

    @property
    def ap_exam(self):
        """Gets the user's AP exam data."""
        if self._ap_exam is None:
            return {}
        return self._ap_exam

    @ap_exam.setter
    def ap_exam(self, ap_exam):
        """Sets the user's AP exam data."""
        self._ap_exam = ap_exam if ap_exam is not None else {}

    @property
    def school(self):
        return self._school

    @school.setter
    def school(self, school):
        self._school = school

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self, inputs=None):
        try:
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            if inputs:
                self.update(inputs)
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        data = {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "email": self.email,
            "sid": self.sid,
            "role": self.role,
            "pfp": self.pfp,
            "kasm_server_needed": self.kasm_server_needed,
            "grade_data": self.grade_data,
            "ap_exam": self.ap_exam,
            "password": self._password,  # Only for internal use, not for API
            "school": self.school
        }
        sections = self.read_sections()
        data.update(sections)
        return data
        
    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self

        name = inputs.get("name", "")
        uid = inputs.get("uid", "")
        email = inputs.get("email", "")
        sid = inputs.get("sid", "")
        password = inputs.get("password", "")
        pfp = inputs.get("pfp", None)
        kasm_server_needed = inputs.get("kasm_server_needed", None)
        grade_data = inputs.get("grade_data", None)
        ap_exam = inputs.get("ap_exam", None)
        school = inputs.get("school", None)
        # States before update
        old_uid = self.uid
        old_kasm_server_needed = self.kasm_server_needed

        # Update table with new data
        if name:
            self.name = name
        if uid:
            self.set_uid(uid)
        if email:
            self.email = email
        if sid:
            self.sid = sid
        if password:
            self.set_password(password)
        if pfp is not None:
            self.pfp = pfp
        if kasm_server_needed is not None:
            self.kasm_server_needed = bool(kasm_server_needed)
        if grade_data is not None:
            self.grade_data = grade_data
        if ap_exam is not None:
            self.ap_exam = ap_exam
        if school is not None:
            self.school = school

        # Check this on each update
        if not email:
            if email == "?":
                self.set_email()

        # Make a KasmUser object to interact with the Kasm API
        kasm_user = KasmUser()

        # Update Kasm server group membership if needed
        if self.kasm_server_needed:
            # UID has changed, delete old Kasm user if it exists
            if old_uid != self.uid:
                kasm_user.delete(old_uid)
            # Create or update the user in Kasm, including a password
            kasm_user.post(self.name, self.uid, password if password else app.config["DEFAULT_PASSWORD"])
            # User is transtioning from non-Kasm to Kasm user, thus it requires posting all groups to Kasm
            if not old_kasm_server_needed:
                kasm_user.post_groups(self.uid, [section.abbreviation for section in self.sections])
        # User is transitioning from Kasm user to non-Kasm user, thus it requires cleanup of defunct Kasm user
        elif old_kasm_server_needed:
            kasm_user.delete(self.uid)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self
    
    # CRUD delete: remove self
    # None
    def delete(self):
        try:
            KasmUser().delete(self.uid)
            db.session.delete(self)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return None   
    
    def save_pfp(self, image_data, filename):
        """For saving profile picture."""
        try:
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], self.uid)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            file_path = os.path.join(user_dir, filename)
            with open(file_path, 'wb') as img_file:
                img_file.write(image_data)
            self.update({"pfp": filename})
        except Exception as e:
            raise e
        
    def delete_pfp(self):
        """Deletes profile picture from user record."""
        self.pfp = None
        db.session.commit()
        
    def add_section(self, section):
        # Query for the section using the provided abbreviation
        found = any(s.id == section.id for s in self.sections)
        
        # Check if the section was found
        if not found:
            # Add the section to the user's sections
            user_section = UserSection(user=self, section=section)
            db.session.add(user_section)
            
            # Commit the changes to the database
            db.session.commit()
        else:
            # Handle the case where the section exists
            print("Section with abbreviation '{}' exists.".format(section._abbreviation))
        # update kasm group membership
        if self.kasm_server_needed:
            KasmUser().post_groups(self.uid, [section.abbreviation])
        return self
    
    def add_sections(self, sections):
        """
        Add multiple sections to the user's profile.

        :param sections: A list of section abbreviations to be added.
        :return: The user object with the added sections, or None if any section is not found.
        """
        # Iterate over each section abbreviation provided
        for section in sections:
            # Query the Section model to find the section object by its abbreviation
            section_obj = Section.query.filter_by(_abbreviation=section).first()
            # If the section is not found, return None
            if not section_obj:
                return None
            # Add the found section object to the user's profile
            self.add_section(section_obj)
        # Return the user object with the added sections
        return self
        
    def read_sections(self):
        """Reads the sections associated with the user."""
        sections = []
        # The user_sections_rel backref provides access to the many-to-many relationship data 
        if self.user_sections_rel:
            for user_section in self.user_sections_rel:
                # This user_section backref "row" can be used to access section methods 
                section_data = user_section.section.read()
                # Extract the year from the relationship data  
                section_data['year'] = user_section.year  
                sections.append(section_data)
        return {"sections": sections} 
    
    def update_section(self, section_data):
        """
        Updates the year enrolled for a given section.

        :param section_data: A dictionary containing the section's abbreviation and the new year.
        :return: A boolean indicating if the update was successful.
        """
        abbreviation = section_data.get("abbreviation", None)
        year = int(section_data.get("year", default_year()))  # Convert year to integer, default to 0 if not found

        # Find the user_section that matches the provided abbreviation through the user_sections_rel backref
        section = next(
            (s for s in self.user_sections_rel if s.section.abbreviation == abbreviation),
            None
        )

        if section:
            # Update the year for the found section
            section.year = year
            db.session.commit()
            return True  # Update successful
        else:
            return False  # Section not found
    
    def remove_sections(self, section_abbreviations):
        """
        Remove sections based on provided abbreviations.

        :param section_abbreviations: A list of section abbreviations to be removed.
        :return: True if all sections are removed successfully, False otherwise.
        """
        try:
            # Iterate over each abbreviation in the provided list
            for abbreviation in section_abbreviations:
                # Find the section matching the current abbreviation
                section = next((section for section in self.sections if section.abbreviation == abbreviation), None)
                if section:
                    # If the section is found, remove it from the list of sections
                    self.sections.remove(section)
                else:
                    # If the section is not found, raise a ValueError
                    raise ValueError(f"Section with abbreviation '{abbreviation}' not found.")
            db.session.commit()
            return True
        except ValueError as e:
            # Roll back the transaction if a ValueError is encountered
            db.session.rollback()
            print(e)  # Log the specific abbreviation error
            return False
        except Exception as e:
            # Roll back the transaction if any other exception is encountered
            db.session.rollback()
            print(f"Unexpected error removing sections: {e}") # Log the unexpected error
            return False
        
    def set_uid(self, new_uid=None):
        """
        Update the user's directory based on the new UID provided.

        :param new_uid: Optional new UID to update the user's directory.
        :return: The updated user object.
        """
        # Store the old UID for later comparison
        old_uid = self._uid
        # Update the UID if a new one is provided
        if new_uid and new_uid != self._uid:
            self._uid = new_uid
            # Commit the UID change to the database
            db.session.commit()

        # If the UID has changed, update the directory name
        if old_uid != self._uid:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_uid)
            new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], self._uid)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)

    def add_stockuser(self):
        """
        Add 1-to-1 stock user to the user's record. 
        """
        if not self.stock_user:
            self.stock_user = StockUser(uid=self._uid, stockmoney=100000)
            db.session.commit()
        return self 
            
    def read_stockuser(self):
        """
        Read the stock user daata associated with the user.
        """
        if self.stock_user:
            return self.stock_user.read()
        return None
    
"""Database Creation and Testing """

# Builds working data set for testing
def initUsers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        
        default_grade_data = {
            'grade': 'A',
            'attendance': 5,
            'work_habits': 5,
            'behavior': 5,
            'timeliness': 5,
            'tech_sense': 4,
            'tech_talk': 4,
            'tech_growth': 4,
            'advocacy': 4,
            'communication_collaboration': 5,
            'integrity': 5,
            'organization': 5
        }

        default_ap_exam = {
            'predicted_score': {
                'practice_based': {
                    'mcq_2018': 0,
                    'mcq_2020': 0,
                    'mcq_2021': 0,
                    'practice_frq': 0,
                    'predicted_ap_score': 0,
                    'confidence_level': 'Low'
                },
                'manual_calculator': {
                    'mcq_score': 60,
                    'frq_score': 6,
                    'composite_score': 90,
                    'predicted_ap_score': 5
                }
            },
            'last_updated': None
        }

        u1 = User(name=app.config['ADMIN_USER'], uid=app.config['ADMIN_UID'], password=app.config['ADMIN_PASSWORD'], pfp=app.config['ADMIN_PFP'], kasm_server_needed=True, role="Admin")
        u2 = User(name=app.config['DEFAULT_USER'], uid=app.config['DEFAULT_UID'], password=app.config['DEFAULT_USER_PASSWORD'], pfp=app.config['DEFAULT_USER_PFP'])
        u3 = User(name='Nicholas Tesla', uid='niko', pfp='niko.png', role='Teacher', password=app.config['DEFAULT_USER_PASSWORD'])


        users = [u1, u2, u3]
        
        for user in users:
            try:
                user.create()
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {user.uid}")

        s1 = Section(name='Computer Science A', abbreviation='CSA')
        s2 = Section(name='Computer Science Principles', abbreviation='CSP')
        s3 = Section(name='Engineering Robotics', abbreviation='Robotics')
        s4 = Section(name='Computer Science and Software Engineering', abbreviation='CSSE')
        sections = [s1, s2, s3, s4]
        
        for section in sections:
            try:
                section.create()    
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {section.name}")
            
        u1.add_section(s1)
        u1.add_section(s2)
        u2.add_section(s2)
        u2.add_section(s3)
        u3.add_section(s4)