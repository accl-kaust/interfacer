import re

pat = 'enable'

string = 'enable_01'

pat = re.compile('.*({}).*'.format(pat))

if re.search(pat, string):
    print('success!')