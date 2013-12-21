#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.utils import formatdate
import mimetypes
import datetime
from pprint import pprint


__all__ = '''
MailBuilder
'''.split()


class MailBuilder:
    def __init__(self):
        self._body = None
        self._subject = None
        self._from_ = None
        self._to = []
        self._attachments = []
        self._date = None

    def body(self, body):
        self._body = body

    def subject(self, subject):
        self._subject = subject

    def from_(self, from_):
        self._from_ = from_

    def to(self, *tos):
        for to in tos:
            if isinstance(to, tuple):
                to = "{} <{}>".format(to[0], to[1])
            self._to.append(to)

    def date(self, date):
        if isinstance(date, datetime.datetime):
            date = int((date - datetime.datetime.utcfromtimestamp(0)).total_seconds())
        self._date = formatdate(date)

    def attach(self, content, filename, mime_type):
        self._attachments.append(Attachment(content, filename, mime_type))

    def attach_file(self, filename, mime_type=None):
        self._attachments.append(Attachment.from_file(filename, mime_type))

    def as_dict(self):
        return {
            'subject': self._subject,
            'body': self._body,
            'from': self._from_,
            'to': self._to,
            'attachments': [a.as_dict() for a in self._attachments]
        }

    def pprint(self):
        pprint(self.as_dict())

    def as_mime(self):
        def set_header(m):
            m['Subject'] = Header(self._subject)
            m['From'] = Header(self._from_)
            m['To'] = Header(', '.join(self._to))

            if self._date is not None:
                m['Date'] = self._date

        if self._attachments:
            m = MIMEMultipart()
            set_header(m)
            m.attach(MIMEText(self._body))

            for a in self._attachments:
                m.attach(a.as_mime())
        else:
            m = MIMEText(self._body)
            set_header(m)
        return m

    def as_eml(self):
        return self.as_mime().as_string()


class Attachment:
    def __init__(self, content, filename, mime_type):
        self._content = content
        self._filename = filename
        self._mime_type = mime_type

    @classmethod
    def from_file(cls, filename, mime_type=None):
        if mime_type is None:
            mime_type = mimetypes.gues_type(filename)
        content = io.open(filename, 'rb').read()
        return cls(content, filename, mime_type)

    def as_mime(self):
        if isinstance(self._mime_type, tuple):
            main_type, sub_type = self._mime_type
        else:
            main_type, sub_type = self._mime_type.split('/', 2)
        m = MIMEBase(main_type, sub_type)
        m.set_payload(self._content)
        m.add_header('Content-Disposition', 'attachment', filename=self._filename)
        encode_base64(m)

        return m


def main():
    # b = MailBuilder()
    # b.to('foo@to.example.com', 'bar@to.example.com')
    # b.from_('from@example.com')
    # b.subject('TITLE')
    # b.body('MESSAGE')
    # b.date(datetime.datetime.now())
    # print(b.as_eml())

    b = MailBuilder()
    b.to('foo@to.example.com', 'bar@to.example.com')
    b.from_('from@example.com')
    b.subject('TITLE')
    b.body('MESSAGE')
    b.attach('foo', 'text', 'text/plain')
    print(b.as_eml())

if __name__ == '__main__':
    main()
