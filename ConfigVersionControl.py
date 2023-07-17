from netmiko import ConnectHandler,exceptions
import logging
import datetime
import difflib
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# create a logger file for logging purposes with logging level set to DEBUG
logging.basicConfig(filename='ssh_log', level=logging.DEBUG)


lab_csr = {
    'device_type': 'cisco_ios',
    'host': '192.168.146.129',
    'username': 'storm',
    # 'global_delay_factor': 20,
    'auth_timeout': 60,
    'use_keys': True,
    'fast_cli': True,
    'key_file': '/root/netmiko/configmaster/controller.pem',
    'disabled_algorithms': dict(pubkeys=['rsa-sha2-512', 'rsa-sha2-256'])
    }


try:
    net_connect = ConnectHandler(**lab_csr)
    print("Connected Successfully")
    cmd_output = net_connect.send_command('show run')
    print(cmd_output)
    # net_connect.disconnect()
    #C:\Users\kwame.asamoah\OneDrive - NTT\Documents\STORM\CODES\PROJECTS\config management\192.168.10.2_2023-07-08.txt
    device_cfg_old = '/root/netmiko/configmaster/' + lab_csr['host'] + '_' + (datetime.date.today() - datetime.timedelta(days = 1)).isoformat() + '.txt'
    
    with open('/root/netmiko/configmaster/' + lab_csr['host'] + '_' + datetime.date.today().isoformat() + '.txt', 'w') as device_cfg_new:
     device_cfg_new.write(cmd_output + '\n')
     
    #Extracting the differences between yesterday's and today's files in HTML format
    with open(device_cfg_old, 'r') as old_file, open('/root/netmiko/configmaster/' + lab_csr['host'] + '_' + datetime.date.today().isoformat() + '.txt', 'r') as new_file:
     difference = difflib.HtmlDiff().make_file(fromlines = old_file.readlines(), tolines = new_file.readlines(), fromdesc = 'Yesterday', todesc = 'Today')

    
    def create_pdf_from_html(html_content, output_pdf):
        pdfkit.from_string(html_content, output_pdf)

        # Assuming you already have the 'difference' variable containing the HTML difference

    output_pdf = lab_csr['host'] + '_' + 'configVersionControl.pdf'  # Specify the output PDF file path

       # Call the function to create the PDF from the HTML difference
    create_pdf_from_html(difference, output_pdf)
    
        
    #Sending the differences via email
    #Defining the e-mail parameters
    fromaddr = 'stormbliss32@gmail.com'
    toaddr = 'stormbliss32@gmail.com'
    
    #More on MIME and multipart: https://en.wikipedia.org/wiki/MIME#Multipart_messages
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = lab_csr['host'] + '_' +  'Configuration Version Control Report' 
    msg.attach(MIMEText(difference, 'html'))
    
    #Sending the email via Gmail's SMTP server on port 587
    server = smtplib.SMTP('smtp.gmail.com', 587)
    
    #SMTP connection is in TLS (Transport Layer Security) mode. All SMTP commands that follow will be encrypted.
    server.starttls()
    
    #Logging in to Gmail and sending the e-mail
    server.login('stormbliss32@gmail.com', 'gimnfxwpibkqyhwq')
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()
    
    
    #End Of Program
    
except exceptions.NetmikoAuthenticationException:
    print(f"Authentication failed on {lab_csr['host']}")
except exceptions.NetmikoTimeoutException:
    print(f"Session timeout on {lab_csr['host']}")
