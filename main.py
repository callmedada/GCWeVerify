from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
# Initialize Firebase app
cred = credentials.Certificate('gcverify-3573b-firebase-adminsdk-845er-debb6ca1bb.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)

# Home page route
@app.route('/adminverify')
def home():
    return render_template('home.html')

# Registration page route
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get the user's email and password from the form
        email = request.form['email']
        password = request.form['password']

        # Register the user with Firebase Authentication
        res_bool, res = register_user(email, password)
        if res_bool:
            message = "Registration successful! A verification email has been sent to your email address."
        else:
            if res:
                return res
            message = "Registration failed. Please try again later."

        return render_template('result.html', message=message)
    else:
        return render_template('reg.html')
# Verify email route
@app.route('/verify_email', methods=['POST'])
def verify_email():
    email = request.form['email']
    try:
        user = auth.get_user_by_email(email)
        if user.email_verified:
            message = "Email is already verified."
        else:
            auth.update_user(user.uid, email_verified=True)
            message = "Email has been successfully verified."
    except Exception as e:
        message = "Error verifying email: {}".format(e)
    return render_template('result.html', message=message)

def register_user(email, password):
    try:
        # Create a new user with the email and password

        if not email.endswith('canada.ca') or not email.endswith('gc.ca') or not email.endswith('ontario.ca'):
            return False, render_template('result.html', message="Email is not a GC email")
        user = auth.create_user(
            email=email,
            password=password
        )
        # Send a verification email to the user
        link = auth.generate_email_verification_link(email, action_code_settings=None)
        message = Mail(
            from_email='zhengc@utoronto.ca',
            to_emails=email,
            subject='GCVerify',
            html_content=link)
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            return True, None
        except Exception as e:
            print(e)
            auth.delete_user(user.uid)
            return False, render_template('result.html', message="Email Send Failed")
        return True
    except Exception as e:
        # Registration failed
        message = "Error verifying email: {}".format(e)
        return False, render_template('result.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
