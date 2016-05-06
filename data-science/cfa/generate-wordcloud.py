import argparse,json
from wordcloud import WordCloud

argparser = argparse.ArgumentParser(description='Wordcloud Generator')
argparser.add_argument('file',nargs=1,help='A simple json file of word to word count')
argparser.add_argument('year',nargs=1,type=int,help='The year to generate')
argparser.add_argument('type',nargs=1,choices=['single','cumulative'])
argparser.add_argument('imagefile',nargs=1,help='The output image filename')
args = argparser.parse_args()
f = open(args.file[0],'r')
data = json.load(f)
f.close()
year = args.year[0]

words = []
if (args.type[0]=='cumulative'):
   wordCount = {}
   for langYear,languageUsed in data.items():
      if (int(langYear)<=year):
         print('processing {}'.format(langYear))
         for word,count in languageUsed.items():
            if (word in wordCount):
               wordCount[word] += count
            else:
               wordCount[word] = count
   for word,count in wordCount.items():
      words.append((word,count))
   
else:
   for langYear,languageUsed in data.items():
      if (year == int(langYear)):
         print('processing {}'.format(langYear))
         for word,count in languageUsed.items():
            words.append((word,count))

wc = WordCloud(width=600,height=450,background_color='white').generate_from_frequencies(words)
wc.to_file(args.imagefile[0])
