import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def notification(toaddr, sessionURL):
    # toaddr -- email address to send to
    # text content to send
    # subject
    host = os.environ.get('EMAIL_HOST')
    port = os.environ.get('EMAIL_PORT')
    fromaddr = os.environ.get('EMAIL_FROM_ADDRESS')
    password = os.environ.get('EMAIL_PASSWORD')

    if host is not None and host != "" and \
            port is not None and port != "" and \
            fromaddr is not None and fromaddr != "" and \
            password is not None and password != "":

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

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg.attach(MIMEText(html, 'html'))

        server = smtplib.SMTP_SSL(host, port)
        server.login(fromaddr, password)
        server.sendmail(fromaddr, toaddr, msg.as_string())
        server.quit()
    else:
        print("Invalid Email host setting! Skip notification.")