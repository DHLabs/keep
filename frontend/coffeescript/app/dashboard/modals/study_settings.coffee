define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette ) ->

    class StudySettingsModal extends Backbone.Modal
        template: _.template( $( '#study-settings-template' ).html() )
        cancelEl: '.btn-primary'

        initialize: ( options ) ->
            @collection = options.collection
            @study = options.study

        delete_event: ( event ) =>
            @collection.remove( @study )
            @study.destroy()
            @close()

        onRender: () =>
            $( '.study-name', @el ).html( @study.get( 'name' ) )
            $( '.study-delete', @el ).click( @delete_event )

    return StudySettingsModal
)