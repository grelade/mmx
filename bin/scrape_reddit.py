import tools
import re
import config as cfg
from datetime import datetime
import os

class scraper:

	def __init__(self,*args,**kwargs):
		self.nopages = kwargs['nopages']
		self.subreddit = kwargs['name']
		self.active = True
		self.currpage = 1
		self.url = "https://old.reddit.com/r/" + self.subreddit + "/"

		self.htmltext=''

		self.app_urls=''
		self.names=''
		self.upvotes=''
		self.comments=''
		self.publdate=''

		self.gethtml()
		self.cells = cfg.metadata_columns
		self.mindex = cfg.metadata_index_columns

	def gethtml(self):
		self.htmltext = tools.geturl(self.url)

		# regex to find urls
		#these_regex = "data-url=\"(.+?)\""
		these_regex = "data-url=\"([^?]+?)\"" # name.jpg?property=121 bug fix
		pattern = re.compile(these_regex)
		self.all_urls = re.findall(pattern,self.htmltext)

		# regex to find names
		names_regex = "data-event-action=\"title\".+?>(.+?)<"
		names_pattern = re.compile(names_regex)
		self.names = re.findall(names_pattern, self.htmltext)

		# regex to identify upvotes
		upvotes_regex = "data-score.+?\"(.+?)\""
		upvotes_pattern = re.compile(upvotes_regex)
		self.upvotes = re.findall(upvotes_pattern,self.htmltext)

		# regex number of comments
		comments_regex = "data-comments-count.+?\"(.+?)\""
		comments_pattern = re.compile(comments_regex)
		self.comments = re.findall(comments_pattern,self.htmltext)

		# regex publication date
		publdate_regex = "data-timestamp.+?\"(.+?)\""
		publdate_pattern = re.compile(publdate_regex)
		self.publdate = re.findall(publdate_pattern,self.htmltext)


	def extract(self):
		record = {}
		currurl = self.all_urls.pop(0)

		record[self.cells['scrape_time']] = int(datetime.timestamp(datetime.now()))
		record[self.cells['scrape_source']] = self.subreddit
		record[self.cells['image_filename']] = os.path.split(currurl)[1]
		record[self.cells['image_title']] = self.names.pop(0)
		record[self.cells['image_upvotes']] = int(self.upvotes.pop(0))
		record[self.cells['no_of_comments']] = int(self.comments.pop(0))
		record[self.cells['image_publ_date']] = int(self.publdate.pop(0))
		record[self.cells['image_url']] = currurl

        # regex to identify extensions
        #ext_regex = "\.(jpg|jpeg|png|gif)"
		ext_regex = "\.("+(''.join(map(lambda x:x+'|',cfg.filetypes))[:-1])+")"
		ext_pattern = re.compile(ext_regex)
		ext = re.findall(ext_pattern,currurl)

		if len(ext)==1: return record
		else: return {}


	def getmeme(self):
		# extract one meme
		if len(self.all_urls)>0:
		    return self.extract()

		# reached self.nopages
		elif self.nopages==self.currpage:
		    self.active = False
		    print("reached page",self.nopages)
		    return {}

		# page ends
		elif self.nopages>self.currpage:
		    regex1 = "next-button.+?\"(.+?)\""
		    pattern1 = re.compile(regex1)
		    link1 = re.findall(pattern1,self.htmltext)

			# is it last page
		    if(len(link1) < 4 and link1[0]=='desktop-onboarding-sign-up__form-note'): # dirty way of identifying last page
		        print("reached subreddits' last page",self.currpage)
		        self.active = False
		        return {}

			# move to next page
		    else:
		        self.url = link1[0]
		        self.currpage += 1
		        self.gethtml()
		        return self.extract()


if __name__ == "__main__":

	parser = argparse.ArgumentParser(prog='scrape tool for reddit')
	# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
	# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
	# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
	# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
	# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
	# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

	args = parser.parse_args()
