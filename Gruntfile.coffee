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
				tasks: [ 'copy:css', 'compass:dist' ]

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
			css:
				expand: true
				cwd: 'frontend/css'
				src: [ '**/*.css' ]
				dest: '<%= pkg.static_dir %>/css'

			# Javascript components specifically go into an intermediary folder
			# due to a two-stage build-process with Require-JS
			components:
				expand: true
				cwd: 'frontend/components'
				src: [ '**/*.js' ]
				dest: 'build/js/vendor'

			font:
				expand: true
				cwd: 'frontend/font'
				src: [ '**/*' ]
				dest: '<%= pkg.static_dir %>/font'

			img:
				expand: true
				cwd: 'frontend/img'
				src: [ '**/*.png', '**/*.jpg', ]
				dest: '<%= pkg.static_dir %>/img'

		requirejs:
			compile:
				options:
					appDir: 'build'
					mainConfigFile: 'build/js/common.js'
					dir: '<%= pkg.static_dir %>'
					modules: [ {
						name: '../common'
						include: [ 'jquery',
								   'app/viz/main',
								   'app/webform/main']
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

	grunt.registerTask( 'build', [ 'copy:components',
								   'copy:css',
								   'copy:font',
								   'copy:img' ] )