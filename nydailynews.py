import sys
import os.path
import requests
from lxml import html
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

def download_page(url):
    r = requests.get(url)
    tree = html.fromstring(r.content)
    return tree

def to_ascii(s):
    return "".join([x for x in s if ord(x) < 128])


def parse_html(html,xpath):
   return html.xpath(xpath['horoscope_body_p'])[0].text
 
def diff(content,f,xpath):
  if os.path.isfile(f):
    fp = open(f)
    data = fp.read()
    fp.close() 
    if data:
      prev_data =  json.loads(data)
      if content != prev_data:
        return content,True
  return "",False     

def update_file(content, f):
    fp = open(f,"w")
    fp.write(json.dumps(content))
    fp.close()
    

def make_table(xpath,content):
    html = "<p>{0}</p></br></br>".format(content)
    return html

def send_email(email_content,to):
    fromaddr = 'scripts.nitinchadha@gmail.com'
    toaddrs = to
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "nydailynews Horoscope Update"
    msg['From'] = fromaddr
    msg['To'] = ",".join(toaddrs)
    part2 = MIMEText(email_content, 'html')
    msg.attach(part2)
    username = 'scripts.nitinchadha@gmail.com'
    password = 'Automatic@123'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.quit()


if __name__ == "__main__":
    try:
        logger.info("Starting .. {0}".format(str(datetime.datetime.now())))
        url = sys.argv[1]
        f = sys.argv[2]
        to = sys.argv[3:]
        html = download_page(url)
        xpath = {
            "horoscope_body_p": '//div[@id="horoscope-body"]/p'
        }
        content = to_ascii(parse_html(html,xpath))
        diff_content,has_changes = diff(content,f,xpath)
        update_file(content,f)
        if has_changes:
            email_content = make_table(xpath,diff_content)
            send_email(email_content,to)
        logger.info("Completed .. {0}".format(str(datetime.datetime.now())))
    except Exception,e:
        logger.exception(str(e))
        print "Exception .. {0}".format(str(e))
        
