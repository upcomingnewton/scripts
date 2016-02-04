import sys
import requests
from lxml import html
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import logging

python songspk.py http://www.songspk.link/ backup_file  email1 email2 email3...
