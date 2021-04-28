# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 4

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "6e!a4^2@ed09ocp)@=sryko%=5hw$1q*3ykk5!(1z21!9+90x^"

# Secret key for signing cookies
SECRET_KEY = "e#c6464=_mlpc5isu0=ce_8vp5ftefs3yyltz6p-a1ljn*jx)@"

# Folders for user uploads
UPLOAD_FOLDER = '{}/uploads/'.format(BASE_DIR)