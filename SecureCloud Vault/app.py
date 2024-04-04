# Flask application that allows users to register, log in, and upload/download files to/from an AWS S3 bucket using boto3. 

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import boto3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define AWS S3 credentials
AWS_ACCESS_KEY_ID = 'AKIATNH6CIQBN5I6FOPG'
AWS_SECRET_ACCESS_KEY = 'o7cbCOWIiRa4VjTxAHFmSeMUmGMSmqIWCAYmy23c'
AWS_BUCKET_NAME = 'secure-cloud-vault'
S3_BASE_URL = f'https://secure-cloud-vault.s3.amazonaws.com/'

# Initialize boto3 S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# User management
login_manager = LoginManager()
login_manager.init_app(app)

# User model
class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

# Routes
@app.route('/')
def index():
    """
    Homepage route.
    """
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route for user registration.
    """
    if request.method == 'POST':
        # Handle user registration form submission
        username = request.form['username']  # Get username from form
        email = request.form['email']  # Get email from form
        password = request.form['password']  # Get password from form
        
        # Here, validate the form data and create a new user
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        
        # After registering the user, redirect them to the login page
        flash('Registration successful! Please log in.')  # Flash message for success
        return redirect(url_for('login'))  # Redirect to login route
    else:
        # If it's a GET request, simply render the registration form
        return render_template('register.html')  # Render registration form template

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for user login.
    """
    if request.method == 'POST':
        # Handle user login form submission
        username = request.form['username']  # Get username from form
        password = request.form['password']  # Get password from form
        
        # Here, authenticate the user by checking credentials against a database
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('upload'))
        
        # create a dummy user and log them in for demonstration purposes for now
        if username == 'demo' and password == 'password':
            user = User()
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('upload'))
        else:
            flash('Invalid username or password. Please try again.')
            return redirect(url_for('login'))
    else:
        # If it's a GET request, simply render the login form
        return render_template('login.html')  # Render login form template


@app.route('/logout')
@login_required
def logout():
    """
    Route for user logout.
    """
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """
    Route for file upload.
    """
    if request.method == 'POST':
        # Handle file upload form submission
        file = request.files['file']  # Get uploaded file from form
        filename = secure_filename(file.filename)  # Secure filename to prevent path traversal attacks
        s3_client.upload_fileobj(file, AWS_BUCKET_NAME, filename)  # Upload file to S3 bucket
        flash('File uploaded successfully!')
    return render_template('upload.html')  # Render file upload form template

@app.route('/download/<filename>')
@login_required
def download(filename):
    """
    Route for file download.
    """
    # Generate pre-signed URL for downloading file from S3
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': AWS_BUCKET_NAME, 'Key': filename},
        ExpiresIn=3600
    )
    return redirect(presigned_url)  # Redirect user to pre-signed URL for file download


if __name__ == '__main__':
    app.run(debug=True)
