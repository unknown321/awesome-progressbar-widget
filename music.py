#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, mpd
import os.path
import os
from cgi import escape
from string import Template
from datetime import timedelta
from optparse import OptionParser
import time
parser = OptionParser()

MUSIC_DIRECTORY = "/media/your_music_directory"
# a template used by naughty to show notifications with cover
TEMPLATE = """by $artist
from $album ($year)
Track #$track, CD $disc, $playlist_track/$total_count"""
COVER_NAMES = ['cover.jpg', "cover.png", "cover.jpeg", "cover.bmp", "folder.jpg", 'Folder.jpg']

def trunc_title(artist, title, duration):
	if (len(str(artist)) + len(str(title))) > 50:
		title = title[:50]
		artist = ""
	else:
		title = " - " + title
	g = Template("$artist$title ($duration)")
	truncated_title = escape(g.substitute(artist=artist, title=title, duration=duration))
	if len(truncated_title) == 0:
		truncated_title = '---'
	return truncated_title


def resize_cover(path):
	# non-square covers are broken when shown by naughty.notify
	# resize to 180x180 with alpha background
	# not a good way to go, but it works
	# called only when a notification raised
	os.popen("convert '{0}' -resize 180x180 -size 180x180 xc:none +swap -gravity center  -composite /tmp/tempcover.png".format(path))	


def connect():
	client = mpd.MPDClient()
	try:
		client.connect("localhost", 6600)
	except Exception,e:
		return None
	else:
		return client


def append_cover(_filepath):
	last_slash = _filepath.rfind('/')
	directory = MUSIC_DIRECTORY + _filepath[:last_slash] + '/'

	cover_name = ""
	for name in COVER_NAMES:
		if os.path.isfile(directory + name):
			cover_name = name
			break
	if cover_name:
		cover = directory + cover_name
	else:
		cover = "/home/unknown/.config/awesome/nocover.png"
		# save_dir(directory)
	return cover

def get_song_info(_client):
	currentsong = _client.currentsong()
	status = _client.status()
	album = currentsong.get('album')
	artist = currentsong.get('artist')
	disc = currentsong.get('disc')
	if not disc:
		disc = 1
	filepath = currentsong.get('file')
	time = currentsong.get('time')
	elapsed = currentsong.get('elapsed')
	title = currentsong.get('title')
	if not title:
		title = ""
	year = currentsong.get('date')
	if not year:
		year = '.'
	track = currentsong.get('track')
	playlist_track = currentsong.get('id')
	total_count = len(_client.playlist())
	return {"currentsong":currentsong, "status":status, "album":album,
			"artist":artist,"disc":disc, "filepath":filepath, "time":time,
			"elapsed":elapsed, "title":title, "year":year, "track":track,
			"playlist_track":playlist_track, "total_count":total_count}


def fill_template(_info):
	text_template = Template(TEMPLATE)
	d = {
		 'artist':_info['artist'],
		 'album':_info['album'],
		 'year':_info['year'],
		 'track':_info['track'],
		 'disc':_info['disc'],
		 'playlist_track':_info['playlist_track'],
		 'total_count':_info['total_count']
		}
	text = text_template.substitute(**d)
	return text


def parse_time(_time):
	if  not _time:
		return "00:00"
	td = timedelta(seconds=int(_time))
	hours, remainder = divmod(td.seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	if hours > 0:
		realtime = "{0:0=2}:{1:0=2}:{2:0=2}".format(hours, minutes, seconds)
	else:
		realtime = "{0:0=2}:{1:0=2}".format(minutes, seconds)
	# fill #1 with zeroes, alignment option '=' (before the digits), 2 symbols total
	return realtime


def print_notification_info(client):
	info = get_song_info(client)
	cover = append_cover(info['filepath'])
	if 'nocover.png' not in cover:
		resize_cover(cover)
		cover = '/tmp/tempcover.png'

	a = {}
	a['notification_text'] = escape(fill_template(info))
	realtime = parse_time(info["time"])
	a['truncated_title'] = trunc_title(info['artist'], info['title'], realtime)
	a['cover'] = cover 											# path to cover
	a['title_time'] = escape(info['title'] + ' (' + realtime + ')')

	return a

def print_progress_info(client):
	a = {'time_text':'00:00'}
	info = get_song_info(client)
	if info.has_key('status'):
		if 'time' in info['status'].keys():
			time_text = info['status']['time']
			realtime = parse_time(info["time"])
			truncated_title = trunc_title(info['artist'], info['title'], realtime)
			a['time_text'] = time_text
			if truncated_title:
				a['truncated_title'] = truncated_title
	return a



def __main__():
	time.sleep(2)
	client = connect()
	mpd_info_file = open('/home/unknown/.config/awesome/mpdinfo','w')
	if not client:
		print "No connection"
		return 1
	while True:
		try:
			client.ping()
		except Exception, e:
			time.sleep(1)
			print "music daemon error {0}".format(str(e))
		else:
			progress = print_progress_info(client)
			for key, value in progress.iteritems():
				mpd_info_file.write(value + '\n')
			if options.NOTIF:
				notification = print_notification_info(client)
				for key, value in notification.iteritems():
					mpd_info_file.write(value + '\n')
				return 0
			mpd_info_file.seek(0,0)
			time.sleep(3)
	# parser.add_option("-p", action="callback", callback=print_progress_info, callback_kwargs={'client':client})
	# parser.add_option("-t", action="callback", callback=print_notification_info, callback_kwargs={'client':client})
	# (options, args) = parser.parse_args()

NOTIF = False
parser.add_option("-n", action='store_true', dest="NOTIF")
(options, args) = parser.parse_args()

if __name__ == '__main__':
	__main__()

sys.exit(0)
