module.exports = ( grunt ) ->

  path = require( 'path' )

  grunt.initConfig
    pkg: grunt.file.readJSON( 'package.json' )

    # Watch files and run the appropriate task on that file when it is
    # changed.
    watch:
      components:
        files: [ 'frontend/components/**/*.js' ]
        tasks: [ 'copy:components', 'coffee:requirejs', 'requirejs' ]

      scripts:
        files: [ 'frontend/coffeescript/**/*.coffee' ]
        tasks: [ 'copy:components', 'coffee:requirejs', 'requirejs' ]

      styles:
        files: [ 'frontend/sass/**/*.scss' ]
        tasks: [ 'sass:dev' ]

      images:
        files: [ 'frontend/img/**/*' ]
        tasks: [ 'copy:img' ]

    # Copy the appropriate bower components to our <vendor> folder
    bower:
      install:
        options:
          targetDir: '<%= pkg.static_dir %>'
          layout: (type, component) ->
            renamedType = type
            if type == 'js'
              renamedType = 'js/vendor'
            else if type == 'css'
              renamedType = 'css'
            else if type == 'font'
              renamedType = 'font'
            return renamedType

    # Compile all javascript and place into our intermediary folder for
    # RequireJS optimization
    coffee:
      requirejs:
        options:
          bare: true
        expand: true
        cwd: 'frontend/coffeescript'
        src: [ '**/*.coffee' ]
        dest: 'build/js'
        ext: '.js'

    sass:
      dev:
        files:
          '<%= pkg.static_dir %>/css/layout.css': 'frontend/sass/layout.scss'
      prod:
        options:
          outputStyle: 'compressed'
        files:
          '<%= pkg.static_dir %>/css/layout.css': 'frontend/sass/layout.scss'

    copy:
      css:
        expand: true
        cwd: 'frontend/css'
        src: [ '**/*' ]
        dest: '<%= pkg.static_dir %>/css'

      # Javascript components specifically go into an intermediary folder
      # due to a two-stage build-process with Require-JS
      components:
        expand: true
        cwd: 'frontend/components'
        src: [ '**/*.js' ]
        dest: 'build/js/vendor'

      favicon:
        expand: true
        cwd: 'frontend/favicon'
        src: [ '**/*' ]
        dest: '<%= pkg.static_dir %>/favicon'

      img:
        expand: true
        cwd: 'frontend/img'
        src: [ '**/*.png', '**/*.jpg' ]
        dest: '<%= pkg.static_dir %>/img'

    requirejs:
      compile:
        options:
          appDir: 'build'
          mainConfigFile: 'build/js/common.js'
          dir: '<%= pkg.static_dir %>'
          keepBuildDir: true
          optimize: if grunt.option('target') and grunt.option('target') is 'prod' then 'uglify' else 'none'
          optimizeCss: 'none'
          modules: [ {
            name: '../common'
            include: [ 'jquery',
                   'app/dashboard/main',
                   'app/dashboard/views',
                   'app/viz/main',
                   'app/viz/views',
                   'app/webform/main',
                   'app/webform/views' ]
          }]


  grunt.loadNpmTasks( 'grunt-bower-task' )
  grunt.loadNpmTasks( 'grunt-contrib-watch' )
  grunt.loadNpmTasks( 'grunt-contrib-requirejs' )
  grunt.loadNpmTasks( 'grunt-contrib-coffee' )
  grunt.loadNpmTasks( 'grunt-sass' )
  grunt.loadNpmTasks( 'grunt-contrib-copy' )

  grunt.registerTask( 'default', [ 'watch' ] )

  # Run through Javascript/CSS compilation process,
  # add --target=prod to minify Javascript assets.
  grunt.registerTask( 'build', [
                   'bower',
                   'copy:components',
                   'coffee:requirejs',
                   'requirejs',

                   # Compile SCSS
                   'sass:dev',

                   # Finally copy oher basic components over to
                   # <static> folder
                   'copy:components',
                   'copy:css',
                   'copy:favicon',
                   'copy:img' ] )
