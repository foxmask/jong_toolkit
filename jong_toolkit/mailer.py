# coding: utf-8
# python lib
import asyncio
import calendar
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from logging import getLogger
import math
import os
import smtplib
from threading import Timer
import time
# joplin api
from joplin_api import JoplinApi

current_folder = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(current_folder, 'settings.ini'))

logging.basicConfig(filename='jong_toolkit.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


if not config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN']:
    raise ValueError('Token not provided, edit the settings.ini and set JOPLIN_WEBCLIPPER_TOKEN accordingly')

if not config['MAIL']['EMAIL_SERVER']:
    raise ValueError('Email server not defined, edit the settings.ini and set EMAIL_SERVER accordingly')


def _send_msg(title, body):
    """

    :param title:
    :param body:
    :return:
    """
    logger.debug("send message to %s title %s" % (config['MAIL']['EMAIL_TO'], title))

    msg = MIMEMultipart('alternative')

    part1 = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
    part2 = MIMEText(body.encode('utf-8'), 'html', 'utf-8')
    msg.attach(part1)
    msg.attach(part2)

    msg['Subject'] = title
    msg['From'] = config['MAIL']['EMAIL_FROM']
    msg['To'] = config['MAIL']['EMAIL_TO']

    with smtplib.SMTP(config['MAIL']['EMAIL_SERVER']) as s:
        s.sendmail(config['MAIL']['EMAIL_FROM'], config['MAIL']['EMAIL_TO'], msg.as_string())


async def mailer():
    todo_due = []
    joplin = JoplinApi(token=config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN'])
    # get all the notes
    res = await joplin.get_notes()
    if res.status_code != 200:
        raise ConnectionError(res.raise_for_status())
    # read all the note
    for note in res.json():
        # just get the todo_due ones
        if note['todo_due'] > 0:
            todo_due.append({'title': note['title'], 'body': note['body'], 'todo_due': note['todo_due']})

    if len(todo_due) > 0:
        # sort all of them by todo_due date
        sorted_x = sorted(todo_due, key=lambda i: i['todo_due'])
        # for each of them, calculate if the date will be due soon
        for data in sorted_x:
            """
            as Timer() only handles 'secondes', have to convert twice,
            to calculate current date and diff between now and todo_due
            """
            # 1 - todo_due is in millisecond, so have to calendar timegm in milliseconds
            now = calendar.timegm(time.gmtime()) * 1000
            # 2 - diff in milliseconds, converted in second
            in_sec = math.ceil((data['todo_due'] - now) / 1000)
            # tododate already due
            if in_sec < 0:
                continue
            else:
                # due date found
                logger.debug("note to send to %s : title %s" % (config['MAIL']['EMAIL_TO'], data['title']))
                # let's mail
                t = Timer(in_sec, _send_msg, args=[data['title'], data['body']])
                t.start()
                t.join()


if __name__ == '__main__':
    print('Jong Toolkit - mailer started!')
    loop = asyncio.get_event_loop()
    try:
        print("Wait for next todo due to be reached")
        loop.run_until_complete(mailer())
    finally:
        loop.close()
