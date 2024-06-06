from flask_mail import Message
from . import mail

def send_welcome_email(email, password):
    msg = Message('Welcome to MissedShots', recipients=[email])
    msg.body = f'''Dear User,

Welcome to MissedShots!

We hope you enjoy using our platform. Here are your account details:
Email: {email}
Password: {password}

Best regards,
The MissedShots Team
    '''
    msg.html = f'''<p style="color: black;">Dear User,</p>
<p style="color: black;">Welcome to MissedShots!</p>
<p style="color: black;">We hope you enjoy using our platform. Here are your account details:</p>
<p style="color: black;">Email: {email}</p>
<p style="color: black;">Password: {password}</p>
<p style="color: black;">Best regards,</p>
<p style="color: black;">The MissedShots Team</p>
    '''
    mail.send(msg)

def send_password_update_email(email, new_password):
    msg = Message('Password Update Notification', recipients=[email])
    msg.body = f'''Dear User,

Your password has been updated successfully.

New Password: {new_password}

Best regards,
The MissedShots Team
    '''
    msg.html = f'''<p style="color: black;">Dear User,</p>
<p style="color: black;">Your password has been updated successfully.</p>
<p style="color: black;">New Password: {new_password}</p>
<p style="color: black;">Best regards,</p>
<p style="color: black;">The MissedShots Team</p>
    '''
    mail.send(msg)
