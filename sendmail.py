import smtplib

def sendmail(IP):
    sender_email = "brysongracias@gmail.com"
    sender_password = "pnuxbuhqcyzeguck"
    receiver_email = "niranjanhebli@nitgoa.ac.in"
    # receiver_email = "gladiatorgracias2016@gmail.com"
    subject = "Road Blocked by Cattle!"
    message = "road blocked by cattle at the following location of the IP camera: "+IP


    def send_email(sender_email, sender_password, receiver_email, subject, message):
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        email_message = f"Subject: {subject}\n\n{message}"

        server.sendmail(sender_email, receiver_email, email_message)

        server.quit()

        print("Email sent successfully!")

    send_email(sender_email, sender_password, receiver_email, subject, message)