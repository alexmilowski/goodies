import argparse,json,requests

def orgs():
   uri = 'http://codeforamerica.org/api/organizations'
   count = 0
   while (uri != None):
      req = requests.get(uri)
      if (req.status_code == 200):
         count += 1
         ruri = uri
         data = req.json()
         uri = data['pages']['next'] if 'next' in data['pages'] else None
         yield count,ruri,data
      else:
         raise IOError('Cannot get uri <{}>, status={}'.format(uri,status))


argparser = argparse.ArgumentParser(description='CFA Organization Downloader')
argparser.add_argument('dir',nargs=1,help='The output directory.')
args = argparser.parse_args()
outDir = args.dir[0]

for count,uri,data in orgs():
   file = outDir + '/orgs-' + str(count) + '.json'
   print('{} → {}'.format(uri,file))
   f = open(file,"w")
   json.dump(data,f)
   f.close()

