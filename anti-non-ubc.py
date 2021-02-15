#!/usr/bin/env python3

from email.parser import Parser
from email.policy import SMTP
from sys import stdin, stdout
import re
import base64
import quopri
import codecs

plaintext_re = re.compile(r"\[CAUTION: Non-UBC Email\]\n\s*\n", re.MULTILINE)
html_re = re.compile(r'<table style="border-collapse: collapse; padding-left: 0px;"><tbody><tr><td><font style="font-family: Arial, sans-serif; font-size: 12px; font-style: normal; font-weight: normal; color: #000000; background-color: #FFECB3; line-height: 1.6; padding: 3px;">\[<strong>CAUTION:</strong> Non-UBC Email\]</font></td></tr></tbody></table>', re.MULTILINE)

def filter(part):
  new_body = re.sub(html_re,'',re.sub(plaintext_re,'',part.get_content()))
  if part.__getitem__("Content-Transfer-Encoding") == "base64":
    return base64.b64encode(new_body)
  elif part.__getitem__("Content-Transfer-Encoding") == "quoted-printable":
    return quopri.encodestring(new_body) 
  else:
    return new_body

def part_loop(parts):
  for part in parts:
    if part.is_multipart():
      part_loop(part.get_content())
    if (part.get_content_type() == 'text/plain') or (part.get_content_type() == 'text/html'):
      part.set_content(filter(part))
  return

prefix = stdin.readline()

message = Parser(policy=SMTP).parse(stdin)

if not message.is_multipart():
  message.set_content(codecs.decode(filter(message),'unicode-escape'))
else:
  part_loop(message.get_payload())

stdout.write(prefix)
stdout.write(str(message))
