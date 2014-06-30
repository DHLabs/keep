define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/study',

          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette, StudyModel ) ->

    class NewStudyModal extends Backbone.Modal
        template: _.template( $( '#new-study-template' ).html() )
        submitEl: '.btn-primary'
        cancelEl: '.btn-cancel'

        clean: () ->
            values =
                name: $( '#study-name' ).val().replace( /^\s+|\s+$/g, "" )
                description: $( '#study-description' ).val().replace( /^\s+|\s+$/g, "" )
                tracker: $( '#study-tracker' ).is( ':checked' )

            return values

        beforeSubmit: () ->

            @cleaned_data = @clean()

            if @cleaned_data[ 'name' ].length == 0
                $( '.error', $( '#study-name' ).parent() ).html( 'Please used a valid study name' )
                return false

        submit: () ->
            study = new StudyModel()
            study.save( @cleaned_data,
                success: ( model, response, options ) =>
                    model.set( {id: response.id} )
                    @collection.add( model ) )

    return NewStudyModal
)
