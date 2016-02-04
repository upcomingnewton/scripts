import sys
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
    updates = {}
    for key in xpath.keys():
        updates[key] = []
        try:
            children = html.xpath(xpath[key])[0].getchildren()
            for x in children:
                link = x.xpath('a[@class="link"]')
                cat = x.xpath('div[@class="category"]')
                if len(link) > 0:
                    href = link[0].attrib['href']
                    name = link[0].text_content()
                    if len(cat) > 0:
                        cat = to_ascii(cat[0].text)
                        updates[key].append({'name':name, 'link': href, 'category':cat})
                    else:
                        updates[key].append({'name':name, 'link': href})
        except Exception,e:
            updates[key] = "ERROR - {0}".format(str(e.args))
    return updates
    
def diff(content,f,xpath):
    new_updates = {}
    has_changes = False
    try:
        fp = open(f)
        prev_data =  json.loads(fp.read())
        fp.close()
    except Exception,e:
        prev_data = {}
    for x in xpath.keys():
        # for this key, check links
        new_updates[x] = []
        if prev_data and x in prev_data:
            prev_links = [t['link'] for t in prev_data[x]]
            for new_content in content[x]:
                if new_content['link'] not in prev_links:
                    new_updates[x].append(new_content)
                    has_changes = True
        else:
            new_updates[x] = content[x][:]
            has_changes = True
    return new_updates,has_changes

def update_file(content, f):
    fp = open(f,"w")
    fp.write(json.dumps(content))
    fp.close()
    

def make_table(xpath,content):
    html = ""
    for x in xpath.keys():
        html += """
            <h3>{0}</h3>
            <table style="border-collapse: collapse;border: 1px solid black;">
                <thead>
                    <tr>
                        <th> Name </th>
                        <th> Link </th>
                        <th> Type </th>
                    </tr>
                </thead>
                <tbody>
            """.format(x)
        for i in content[x]:
            html += """
                        <tr>
                            <td>{0}</td>
                            <td><a href="{1}">Link</a></td>
                            <td>{2}</td>
                        </tr>
                """.format(i["name"],i["link"],i.get("category"))   
        html += """
                </tbody>
            </table>
            <br /><br />
        """
    return html

def send_email(email_content,to):
    fromaddr = 'scripts.nitinchadha@gmail.com'
    toaddrs = to
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "SongsPK Update"
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
        print "Starting .. {0}".format(str(datetime.datetime.now()))
        url = sys.argv[1]
        f = sys.argv[2]
        to = sys.argv[3:]
        html = download_page(url)
        xpath = {
            "album_update": '//ul[@class="songs-list1"]',
            "single_track_update": '//ul[@class="songs-list11"]'
        }
        content = parse_html(html,xpath)
        diff_content,has_changes = diff(content,f,xpath)
        update_file(content,f)
        if has_changes:
            email_content = make_table(xpath,diff_content)
            send_email(email_content,to)
        print "Completed .. {0}".format(str(datetime.datetime.now()))
    except Exception,e:
        logger.exception(str(e))
        print "Exception .. {0}".format(str(datetime.datetime.now()))
        