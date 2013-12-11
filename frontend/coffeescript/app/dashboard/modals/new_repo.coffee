define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette ) ->

    class NewDiaryModal extends Backbone.Modal

        template: _.template( $( '#file-dropped-template' ).html() )
        submitEl: '.btn-primary'
        cancelEl: '.btn-cancel'

        _detect_file_type: () ->
            # Detect the file type and determine what options we present
            # to the user upon uploading the file.

            if @file.type == 'text/csv'
                @file_type = 'CSV'
            else if @file.type == 'text/xml'
                @file_type = 'XForm'
            else if @file.type == 'application/vnd.ms-excel'
                @file_type = 'Excel'
            else
                @file_type = 'unknown'

            @

        initialize: ( options ) ->

            @studies = options.studies

            # TODO: Handle multiple files?
            @file = options.files[0]
            @_detect_file_type()

            @success_callback = if options.success? then options.success else null
            @error_callback   = if options.error? then options.error else null

            @

        serializeData: () ->

            data =
                file: @file
                studies: @studies.models
                repo_name: @file.name[0..@file.name.length-5]

            return data

        submit: () ->

            data = new FormData()
            data.append( 'repo_file', @file )
            data.append( 'user', document.user )
            data.append( 'tracker', $( 'input[name="tracker"]', @el ).is( ':checked' ) )

            if $( 'select', @el ).val()?
                data.append( 'study', $( 'select', @el ).val() )

            $.ajax(
                url: '/api/v1/repos/'
                data: data
                cache: false
                contentType: false
                processData: false
                headers:
                    'X-CSRFToken': $.cookie( 'csrftoken' )
                type: 'POST'
                success: @success_callback
                error: @error_callback
            )

    return NewDiaryModal
)