import argparse,os,json

argparser = argparse.ArgumentParser(description='CFA Organization Downloader')
argparser.add_argument('dir',nargs=1,help='The data directory.')
args = argparser.parse_args()
dataDir = args.dir[0]

byProject = {}

for file in [dataDir + '/' + f for f in os.listdir(dataDir) if f.startswith('orgs') and f.endswith('.json') and os.path.isfile(dataDir + '/' + f)]:
   print('{}:'.format(file))
   f = open(file,"r")
   data = json.load(f)
   f.close()

   for org in data['objects']:
      #print(org['name'])
      org_api = org['api_url']
      org_name = org['name']
      for project in org['current_projects']:
         languages = project['languages']
         api = project['api_url']
         code = project['code_url']
         if (project['github_details'] == None):
            continue
         if (code == None):
            if ('html_url' in project['github_details']):
               code = project['github_details']['html_url']
            else:
               raise Exception('Project {} for {} has node code url'.format(api,org_name))
         key = None
         for base in ['https://github.com/','http://github.com/']:
            index = code.find(base)
            if (index==0):
               key = code[len(base):]
               break
         if (key == None):
            raise Exception('Cannot generate key for {}'.format(api))
         createdAt = project['github_details']['created_at']
         year = createdAt[:4]
         participation = project['github_details']['participation']
         quarters = [ sum(participation[0:13]), sum(participation[13:26]), sum(participation[26:39]), sum(participation[39:52]) ]
         byProject[key] = { 'organization' : org_name, 'org_api' : org_api, 'api' : api, 'code' : code, 'year' : year, 'created' : createdAt, 'activity' : quarters, 'languages' : languages }

output = open(dataDir + '/participation-by-project.json','w')
json.dump(byProject,output)
output.close()

