from distutils.core import setup
import os
import sys
import shutil

if 'sdist' in sys.argv:
	if not os.path.exists('dist'):
		os.makedirs('dist')
	shutil.copyfile('caduceus.py', 'dist/caduceus')


setup(	name='caduceus',
		version='1.0',
		description='Caduceus generator',
		author='Alexandre Prudent',
		author_email='nobody@nowhere',
		url='http://github.com/aprudent/caduceus',
		license='Simplified BSD',
		
		packages=['caduceus.transform',
				  'caduceus.report',
				  'caduceus',
				  ],
		package_data={'caduceus': ['resources/*.*']},
		
		#py_modules=[''],
		scripts=['dist/caduceus']
		)
