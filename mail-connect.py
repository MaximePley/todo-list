import smtplib

server = smtplib.SMTP()
server.connect('smtp.googlemail.com', '587')
server.ehlo()
server.starttls()
server.login('pleymaxime@gmail.com', 'XXX')
