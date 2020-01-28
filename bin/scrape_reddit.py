# reddit scrape tool
# modified version of https://github.com/Salil-Jain/memescraper
# grelade 2020

import urllib
import re
import subprocess
import time
import sys
import os.path
import os
import pandas as pd
import argparse
import numpy as np

import config as cfg

parser = argparse.ArgumentParser(prog='scrape tool for reddit')
parser.add_argument('--subreddit',type=str,default='memes')
parser.add_argument('--nopages',type=int,default=10)
parser.add_argument('--time',type=str,default='2020-01-01_00:00')
parser.add_argument('--datadir',type=str,default=cfg.default_datadir)
parser.add_argument('--timelag',type=int,default=5)
args = parser.parse_args()


#times = time.strftime("%Y-%m-%d_%H:%M", time.localtime())

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

dataset_meta = pd.DataFrame(columns=[	cells['id'],
										cells['scrape_time'],
										cells['scrape_source'],
										cells['image_filename'],
										cells['image_title'],
										cells['image_upvotes']])

# metadata files are stored in file datadir/time/subreddit.tsv
mdpath = os.path.join(args.datadir,args.time,args.subreddit+'.tsv')
# datasets are stored in datadir/time/subreddit
memedir = os.path.join(args.datadir,args.time,args.subreddit)

# check datadir
if (not os.path.isdir(args.datadir)):
	subprocess.call('mkdir '+args.datadir,shell=True)

# check timedir
dir1 = os.path.join(args.datadir,args.time)
if (not os.path.isdir(dir1)):
	subprocess.call('mkdir '+dir1,shell=True)

# check memedir
if (not os.path.isdir(memedir)):
	subprocess.call('mkdir '+memedir,shell=True)


#the url of the website to be scraped!
urls = "https://old.reddit.com/r/" + args.subreddit + "/"

def savelog(log,logpath):
	print("saving metadata file")
	log = log.set_index(mindex)
	log.to_csv(logpath,mode = 'w',sep='\t')



def geturl(urls):
	print('geturl URL:',urls)
	htmltext = ''
	ifsuccesful = False
	tries = 0
	limit = 25
	while not ifsuccesful and tries < limit:
		try:
			htmlfile = urllib.request.urlopen(urls)
			htmltext = htmlfile.read().decode("utf-8")
			ifsuccesful = True

		except urllib.error.HTTPError:
			print('reached connection limit: sleeping')
			time.sleep(args.timelag)
			tries = tries + 1
			continue
		except ValueError:
			print('ValueError detected!')
			tries = tries + 1
			continue
	return htmltext

# page iterable
i = 0
# index iterable
k = 0
num = args.nopages

try:

	while i < num:

		htmltext = geturl(urls)

		# regex to find urls
		these_regex = "data-url=\"(.+?)\""
		pattern = re.compile(these_regex)
		all_urls = re.findall(pattern,htmltext)

		# regex to find names
		names_regex = "data-event-action=\"title\".+?>(.+?)<"
		names_pattern = re.compile(names_regex)
		names = re.findall(names_pattern, htmltext)

		# regex to identify upvotes
		upvotes_regex = "data-score.+?\"(.+?)\""
		upvotes_pattern = re.compile(upvotes_regex)
		upvotes = re.findall(upvotes_pattern,htmltext)

		# regex number of comments
		comments_regex = "data-comments-count.+?\"(.+?)\""
		comments_pattern = re.compile(comments_regex)
		comments = re.findall(comments_pattern,htmltext)

		# regex publication date
		publdate_regex = "data-timestamp.+?\"(.+?)\""
		publdate_pattern = re.compile(publdate_regex)
		publdate = re.findall(publdate_pattern,htmltext)

		# check for any mismatches in the feed
		if not (len(all_urls)==len(names)==len(upvotes)==len(comments)==len(publdate)):
			print('dimensional mismatch: ',len(all_urls),len(names),len(upvotes),len(comments),len(publdate))
			break

		for j,s in enumerate(all_urls):

			# regex to identify extensions
			#ext_regex = "\.(jpg|jpeg|png|gif)"
			ext_regex = "\.("+(''.join(map(lambda x:x+'|',cfg.filetypes))[:-1])+")"
			ext_pattern = re.compile(ext_regex)
			ext = re.findall(ext_pattern,s)

			if len(ext) == 1:
				memefile = str(np.abs(np.random.randn()))[:10] + "." + ext[0]
				com = "wget --no-check-certificate " + s + " -O \""+ os.path.join(memedir,memefile) + "\""
				subprocess.call(com,shell=True,timeout=50)


				dataset_meta = dataset_meta.append({cells['id']:k,
														cells['scrape_time']:args.time,
														cells['scrape_source']:args.subreddit,
														cells['image_filename']:memefile,
														cells['image_title']:names[j],
														cells['image_upvotes']:upvotes[j],
														cells['no_of_comments']:comments[j],
														cells['image_publ_date']:publdate[j]},
														ignore_index=True)
				k = k+1
				#time.sleep(args.timelag)


		regex1 = "next-button.+?\"(.+?)\""
		pattern1 = re.compile(regex1)
		link1 = re.findall(pattern1,htmltext)
		if(len(link1) < 4 and link1[0]=='desktop-onboarding-sign-up__form-note'):
			print("reached subreddits' last page",i)
			break
		else:
			urls = link1[0]
			#times = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
			#log = log.append(other = pd.Series([urls,times],index=log.columns),ignore_index = True)
			i += 1

	savelog(dataset_meta,mdpath)

except KeyboardInterrupt as e:
	print(e)
	savelog(dataset_meta,mdpath)
