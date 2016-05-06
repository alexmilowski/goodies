import argparse,os,json

argparser = argparse.ArgumentParser(description='CFA Organization Downloader')
argparser.add_argument('dir',nargs=1,help='The data directory.')
args = argparser.parse_args()
dataDir = args.dir[0]

byYear = {}

for file in [dataDir + '/' + f for f in os.listdir(dataDir) if f.startswith('orgs') and f.endswith('.json') and os.path.isfile(dataDir + '/' + f)]:
   print('{}:'.format(file))
   f = open(file,"r")
   data = json.load(f)
   f.close()

   for org in data['objects']:
      #print(org['name'])
      for project in org['current_projects']:
         languages = project['languages']
         if (languages == None):
            continue
         createdAt = project['github_details']['created_at']
         year = createdAt[:4]
         languagesUsed = None
         if year in byYear:
            languagesUsed = byYear[year]
         else:
            languagesUsed = {}
            byYear[year] = languagesUsed
         for language in languages:
            languagesUsed[language] = (languagesUsed[language] + 1) if (language in languagesUsed) else 1

output = open(dataDir + '/languages.json','w')
json.dump(byYear,output)
output.close()

years = [y for y in byYear.keys()]
years.sort()
print(years)
