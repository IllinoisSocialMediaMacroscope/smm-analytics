import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def notification(toaddr, sessionURL):
    # toaddr -- email address to send to
    # text content to send
    # subject
    host = 'smtp.mail.us-east-1.awsapps.com'
    port = '465'
    fromaddr = 'smile@socialmediamacroscope.awsapps.com'

    html = """<html> 
                <head></head>
                <body style="font-size:15px;font-fiamily:'Times New Roman', Times, serif;">
                    <div>
                        <p>Dear user (session ID: """ + sessionURL + """),</p>
                        <p>Your Brand Personality Analysis is successfully finished! Go to the History section of 
                        your BAE session to view the results.</p>
                        <br>
                        <p>Best Regards,</p>
                        <p>Social Media Macroscope - SMILE </p>
                    </div>
                </body>
        </html>"""
    subject = 'Your Brand Personality Analysis is finished!'

    with open('email_password.txt') as f:
        password = f.readlines()[0]

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP_SSL(host, port)
    server.login(fromaddr, password)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()
