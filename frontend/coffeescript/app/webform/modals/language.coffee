define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'backbone_modal',
          'jqueryui',
          'jquery_cookie' ],

( $, _, Backbone, Marionette ) ->

    class LanguageSelectModal extends Backbone.Modal
        template: _.template( $( '#language-select' ).html() )
        submitEl: '.btn-primary'
        cancelEl: '.btn-cancel'

        initialize: ( options ) ->

            @current_language = options.current
            @callbackobject = options.view

        onAfterRender: ( modal ) ->
          $( 'input[value=' + @current_language + ']', modal ).prop('checked',true)

        submit: () ->

            language  = $( 'input[name=language]:checked', @el ).val()
            @callbackobject.change_language(language)

            @

    return LanguageSelectModal

)