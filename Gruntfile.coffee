module.exports = ( grunt ) ->

	grunt.initConfig
		pkg: grunt.file.readJSON( 'package.json' )

		# Watch files and run the appropriate task on that file when it is
		# changed.
		watch:
			scripts:
				files: [ 'frontend/coffeescript/**/*.coffee' ]
				tasks: [ 'coffee' ]

			styles:
				files: [ 'frontend/sass/**/*.scss' ]
				tasks: [ 'compass:dist' ]


		coffee:
			glob_to_multiple:
				options:
					bare: true
				expand: true
				cwd: 'assets/coffee'
				src: [ '**/*.coffee' ]
				dest: 'dist/js'
				ext: '.js'

		compass:
			dist:
				options:
					sassDir: 'assets/sass'
					cssDir: 'dist/css'
					outputStyle: 'compressed'

		copy:
			html:
				expand: true
				cwd: 'assets/templates'
				src: [ '**/*.html' ]
				dest: 'dist'

		uglify:
			options:
				banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
			build:
				src: 'assets/js/<%= pkg.name %>.js'
				dest: 'dist/js/<%= pkg.name %>.min.js'

	grunt.loadNpmTasks( 'grunt-contrib-watch' )
	grunt.loadNpmTasks( 'grunt-contrib-uglify' )
	grunt.loadNpmTasks( 'grunt-contrib-coffee' )
	grunt.loadNpmTasks( 'grunt-contrib-compass' )
	grunt.loadNpmTasks( 'grunt-contrib-copy' )

	grunt.registerTask( 'default', [ 'watch' ] )