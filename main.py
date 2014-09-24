# This file is part of newsfrbot.
# 
# Newsfrbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
# 
# Newsfrbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# (C) Copyright Yves Quemener, 2012

import sources.rue89
import sources.lemonde
import sources.lefigaro
import feedparser
import cPickle
import praw

import traceback
import sys
import getpass
import urllib2

from time import *

# TODO : improve the "database" system that will get corrupted if interrupted and take o(n) time with n=entries already published

reddit = praw.Reddit(user_agent='Newsfr bot, by u/keepthepace')
user='newsfrbot'
print "Password for",user,"?"
passwd=getpass.getpass()
reddit.login(user, passwd)

with open("already_published", "rb") as f:
    already_published = cPickle.load(f)

while True:
    try:

        rue89feed = sources.rue89.get()
        lemondefeed = sources.lemonde.get()
        lefigarofeed = sources.lefigaro.get()
        
        for d in [('lefigaro', lefigarofeed), ('lemonde', lemondefeed), ('rue89', rue89feed)]:
        #for d in [('lemonde', lemondefeed), ('rue89', rue89feed)]:
            for e in d[1]:
                if not e['link'] in already_published:
                    try:
                        print asctime(), "Publishing on",d[0],":", e['title']
                        reddit.submit(d[0], e['title'], url=e['link'])
                        sleep(10) # To comply with reddit's policy : no more than 0.5 req/sec
                        already_published.add(e['link'])
                        with open("already_published", "wb") as f:
                            cPickle.dump(already_published, f)
                    except praw.errors.APIException as ex:
                        if ex.error_type=='ALREADY_SUB':
                            already_published.add(e['link'])
                            print "Already published :", e['title']
                            with open("already_published", "wb") as f:
                                cPickle.dump(already_published, f)
                        else:
                            print asctime(),"Exception : Reddit offline ? Retrying in 5 minutes"
                            traceback.print_stack()
                            print ex.error_type
                            print ex.message
                            print ex.field
                            print ex.response
                            print "_", sys.exc_info()[0]
                            sleep(300)
    except:
        print asctime(),"Exception in main program : "
        traceback.print_exc()
    sleep(300)


