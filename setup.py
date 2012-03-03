from distutils.core import setup
setup(	name='caduceus',
		version='1.0',
		description='Caduceus generator',
		author='Alexandre Prudent',
		author_email='padragn@gmail.com',
		url='http://github.com/aprudent/caduceus',
		
		packages=['caduceus',
				  'caduceus.transform',
				  'caduceus.report',
				  ],		
		package_dir = {'caduceus': '.',
					   'caduceus.transform': './transform',
					   'caduceus.report': './report',
					   },
		package_data={'caduceus': ['resources/*.*']},
		#py_modules=[''],
		scripts=['caduceus.py']
		)