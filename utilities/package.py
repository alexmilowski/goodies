import argparse
import site
import zipfile
import os
import sys

parser = argparse.ArgumentParser(description='packages program in zip')
parser.add_argument('--module',dest='modules',action='append')
parser.add_argument('--main')
parser.add_argument('zip',help='The output zip file')
parser.add_argument('files',nargs='*',help='The main program.')

args = parser.parse_args()

def files(parent,dir):
   queue = [(parent+'/'+dir,dir)]
   while len(queue)>0:
      current_dir,target_dir = queue[0]
      queue = queue[1:]
      for file in os.listdir(current_dir):
         if file=='__pycache__':
            continue
         target = current_dir+'/'+file
         if os.path.isdir(target):
            queue.append((target,target_dir+'/'+file))
         else:
            yield target_dir+'/'+file

with zipfile.ZipFile(args.zip,'w') as zip:
   if args.main is not None:
      print('Adding __main__.py')
      main_py = '''
import sys
from {main} import main
main()
'''.format(main=args.main)
   zip.writestr('__main__.py',main_py)

   for file in args.files:
      print('Adding {}'.format(file))
      zip.write(file)

   for module in args.modules:
      print('Adding module {}:'.format(module))
      for dir in sys.path:
         # zip files are not currently supported so they are skipped
         if not os.path.isdir(dir):
            continue
         found = False
         for entry in os.listdir(dir):
            if entry==module:
               found = True
               os.chdir(dir)
               for file in files(dir,entry):
                  print('Adding {}'.format(file))
                  zip.write(file)
         if found:
            break
