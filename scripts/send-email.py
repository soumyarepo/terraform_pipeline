#!/usr/bin/env python3
import os, smtplib, ssl, sys
from email.message import EmailMessage

html_file, subject = sys.argv[1], sys.argv[2]
required = ["SMTP_HOST","SMTP_PORT","SMTP_USERNAME","SMTP_PASSWORD","EMAIL_FROM","EMAIL_TO"]
missing = [x for x in required if not os.getenv(x)]
if missing:
    raise SystemExit("Missing required email secrets: " + ", ".join(missing))

with open(html_file, encoding="utf-8") as f:
    body = f.read()

msg = EmailMessage()
msg["Subject"] = subject
msg["From"] = os.environ["EMAIL_FROM"]
msg["To"] = os.environ["EMAIL_TO"]
msg.set_content("Terraform deployment completed successfully. View this message in an HTML-capable email client.")
msg.add_alternative(body, subtype="html")

host = os.environ["SMTP_HOST"]
port = int(os.environ["SMTP_PORT"])
user = os.environ["SMTP_USERNAME"]
password = os.environ["SMTP_PASSWORD"]

if port == 465:
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)
else:
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(user, password)
        smtp.send_message(msg)

print("Deployment email sent successfully.")
