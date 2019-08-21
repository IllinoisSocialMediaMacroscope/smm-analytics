import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def lambda_handler(event, context):
    host = 'smtp.mail.us-east-1.awsapps.com'
    port = '465'
    fromaddr = 'smile@socialmediamacroscope.awsapps.com'

    command = event['detail']['container']['command']
    if "--email" in command \
            and "@" in command[command.index("--email") + 1]:
        toaddr = command[command.index("--email") + 1]
    else:
        toaddr = "srti-lab@illinois.edu"

    password = os.environ['password']
    subject = "SMM batch job failed"
    job_name = event['detail']['jobName']
    job_id = event['id']

    html = """<html> 
                    <head></head>
                    <body style="font-size:15px;font-fiamily:'Times New Roman', Times, serif;">
                        <div>
                            <p>Dear user,</p>
                            <p>We are sorry to inform you that your batch <b>job """ + job_id + """</b> (job name: """ + job_name + """) just failed.
                            Please first verify your input parameters are correct. To report your error, go to 
                            <a href="https://socialmediamacroscope.org/feedback/report_problems" target="_blank">
                            https://socialmediamacroscope.org/feedback/report_problems</a></p>
                            <br>
                            <p>Best Regards,</p>
                            <p>Social Media Macroscope - SMILE </p>
                        </div>
                    </body>
            </html>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP_SSL(host, port)
    server.login(fromaddr, password)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()

    return {
        'statusCode': 200,
        'body': json.dumps('Batch Job Failed')
    }
