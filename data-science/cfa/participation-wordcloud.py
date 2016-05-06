import argparse,json,math
from wordcloud import WordCloud

argparser = argparse.ArgumentParser(description='Wordcloud Generator')
argparser.add_argument('file',nargs=1,help='participation data')
argparser.add_argument('range',nargs=1,type=int,choices=[1,2,3,4])
argparser.add_argument('imagefile',nargs=1,help='The output image filename')
argparser.add_argument('quartile',nargs='+',type=int,choices=[1,2,3,4])
args = argparser.parse_args()
f = open(args.file[0],'r')
data = json.load(f)
f.close()
top = args.range[0]

def median(points):
   mid = round(len(points) / 2)
   return (points[mid - 1] + points[mid] / 2.0) if (len(points) % 2 == 0) else points[mid]

activity = []
for key,project in data.items():
   total = sum(project['activity'][0:top])
   if (total>0):
      activity.append(total)

activity.sort()
mid = round(len(activity) / 2)
quartiles = [ median(activity[:mid]), median(activity), median(activity[mid:]), float('inf') ] if (len(activity) % 2 == 0) else [ median(activity[:mid]), median(activity), median(activity[mid+1:]), float('inf')]

print(quartiles)

partitions = []
for quartile in args.quartile:
   partition = (0 if quartile==1 else quartiles[quartile-2],quartiles[quartile-1])
   print(partition)
   partitions.append(partition)

words = []
for key,project in data.items():
   total = sum(project['activity'][0:top])
   for partition in partitions:
      if (total>partition[0] and total<=partition[1]):
         words.append((key.split('/')[1],total))
         
wc = WordCloud(width=600,height=450,background_color='white').generate_from_frequencies(words)
wc.to_file(args.imagefile[0])
