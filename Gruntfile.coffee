module.exports = ( grunt ) ->

	grunt.initConfig
		pkg: grunt.file.readJSON( 'package.json' )

		# Watch files and run the appropriate task on that file when it is
		# changed.
		watch:
			scripts:
				files: [ 'frontend/coffeescript/**/*.coffee' ]
				tasks: [ 'bower', 'copy:components', 'coffee', 'requirejs' ]

			styles:
				files: [ 'frontend/sass/**/*.scss' ]
				tasks: [ 'compass:dist' ]


		bower:
			dev:
				dest: 'build/js/vendor'

		coffee:
			glob_to_multiple:
				options:
					bare: true
				expand: true
				cwd: 'frontend/coffeescript'
				src: [ '**/*.coffee' ]
				dest: 'build/js'
				ext: '.js'

		compass:
			dist:
				options:
					sassDir: 'frontend/sass'
					cssDir: '<%= pkg.static_dir %>/css'
					outputStyle: 'compressed'

		copy:
			components:
				expand: true
				cwd: 'frontend/components'
				src: [ '**/*.js' ]
				dest: 'build/js/vendor'

			html:
				expand: true
				cwd: 'frontend/templates'
				src: [ '**/*.html' ]
				dest: '<%= pkg.static_dir %>/templates'


		requirejs:
			compile:
				options:
					appDir: 'build'
					mainConfigFile: 'build/js/common.js'
					dir: 'release'
					removeCombined: true
					modules: [ {
						name: '../common'
						include: [ 'jquery', 'app/viz/main', 'app/webform/main']
					},{
						name: 'app/viz/main'
						exclude: [ '../common' ]
					},{
						name: 'app/webform/main'
						exclude: [ '../common' ]
					}]

	grunt.loadNpmTasks( 'grunt-bower' )
	grunt.loadNpmTasks( 'grunt-contrib-watch' )
	grunt.loadNpmTasks( 'grunt-contrib-requirejs' )
	grunt.loadNpmTasks( 'grunt-contrib-coffee' )
	grunt.loadNpmTasks( 'grunt-contrib-compass' )
	grunt.loadNpmTasks( 'grunt-contrib-copy' )

	grunt.registerTask( 'default', [ 'watch' ] )