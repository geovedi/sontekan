# Make iPython works in virtualenv.
# This file goes to ~/.ipython/profile_default/startup/

import site
from os import environ
from os.path import join
import sys

if 'VIRTUAL_ENV' in environ:
	virtual_env = join(environ.get('VIRTUAL_ENV'),
		'lib',
		'python%d.%d' % sys.version_info[:2],
		'site-packages')
	
	prev_sys_path = list(sys.path)
	site.addsitedir(virtual_env)

	new_sys_path = []
	for item in list(sys.path):
		if item not in prev_sys_path:
			new_sys_path.append(item)
			sys.path.remove(item)
	sys.path[1:1] = new_sys_path

	print 'Virtual Env    :', virtual_env
	del virtual_env