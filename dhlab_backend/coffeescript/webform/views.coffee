# TODO
#   - Handle xform bindings
#       - Required
#       - Constraints
#       - etc
#
#
define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'vendor/forms/backbone-forms.min',
          'models',
          'builder',
          'constraints' ],

( $, _, Backbone, Forms, xFormModel, build_form, XFormConstraintChecker ) ->

    class xFormView extends Backbone.View
        # The HTML element where the form will be rendered
        el: $( '#webform' )

        # Current form this view is representing
        model: new xFormModel()

        events:
            'click #submit_btn':        'submit'
            'click #form_sidebar > li': 'switch_question'
            'click #next_btn':          'next_question'
            'click #prev_btn':          'prev_question'

        _fieldsets: []
        _data:      []
        _schema:    {}
        item_dict:  {}
        input_fields: []
        renderedForm: null
        languages:  []

        initialize: ->
            # Grab the form_id from the page
            @form_id  = $( '#form_id' ).html()
            @user     = $( '#user' ).html()

            # Begin render when the model is finished fetching from the server
            @listenTo( @model, 'change', @render )
            @model.fetch( { url: "/api/v1/repos/#{@form_id}/?user=#{@user}&format=json" } )

            @

        submit: ->
            $( @renderedForm.el ).submit()

        recursiveAdd: build_form

        render: () ->
            #     groupBegin: '<div class="well"><div><strong>Group: </strong>{{title}}</div></div>'
            #     groupEnd: '<div><hr></div>'

            # Creates submission page, takes care of corner case
            submitChild =
              bind:
                readonly: "true()"

              label: "Form Complete!  Click Submit, or hit Previous to review your answers."
              name: "knozr563kj04tyn748945"
              type: "note"

            @model.attributes.children.push submitChild

            # Create the form to render
            _.each( @model.attributes.children, ( child ) =>
                @recursiveAdd( child, @model.attributes.default_language )
            )

            console.log( @languages )

            # Create the Form object with the schema we want
            @renderedForm = new Backbone.Form(
                schema: @item_dict
                data:   @_data
                fields: @_fieldsets
            ).render()

            _.each( @item_dict, ( child, key ) =>
                child.name = key
                @input_fields.push( child )
            )

            # Render it on the page!
            $('#formDiv').html( @renderedForm.el )

            $( '.control-group' ).first().show().addClass( 'active' )
            $( '.active input' ).focus()

            @_display_form_buttons( 0 )
            @

        _display_form_buttons: ( question_index ) ->

            if question_index == @input_fields.length - 1
                $( '#prev_btn' ).show()
                $( '#submit_btn' ).show()

                $( '#next_btn' ).hide()
            else if question_index == 0
                $( '#prev_btn' ).hide()
                $( '#submit_btn' ).hide()

                $( '#next_btn' ).show()
            else
                $( '#prev_btn' ).show()
                $( '#next_btn' ).show()

                $( '#submit_btn' ).hide()

            @

        _active_question: ->
            # First check constraints on the question we're on
            question = $( '.active' ).data( 'key' )

            # Check constraints of this question before continuing
            question_index = -1
            form_info = _.find( @input_fields, ( child ) ->
                question_index += 1
                return child.name == question
            )

            return { 'key': question, 'idx': question_index, 'info': form_info }

        passes_question_constraints: ->
            # First check constraints on the question we're on
            question = @_active_question()

            # Pass required?
            if question.info.bind and question.info.bind.required is "yes"
                if @renderedForm.getValue()[ question.key ].length == 0
                    alert "Answer is required"
                    return false

            # Pass contraints?
            if not XFormConstraintChecker.passesConstraint( question.info, @renderedForm.getValue() )
                alert "Answer doesn't pass constraint:" + question.info.bind.constraint
                return false

            return true

        switch_question: ( element, forward ) ->

            # Does the current active question pass our constraints?
            if forward
                if not @passes_question_constraints()
                    return @

            # Current question
            current_question = @_active_question()

            # Question to switch to
            switch_question_key = $( element ).data( 'key' )

            # Check constraints of this question before continuing
            question_index = -1
            form_info = _.find( @input_fields, ( child ) ->
                question_index += 1
                return child.name == switch_question_key
            )

            # Is this question relevant?
            if not XFormConstraintChecker.isRelevant( form_info, @renderedForm.getValue() )

                # Switch to the next question!
                if forward
                    if question_index < @input_fields.length
                        question_index += 1
                else
                    if question_index > 0
                        question_index -= 1

                @switch_question( $( '.control-group' ).eq( question_index ), forward )
                return

            # Find the next question to switch from and to.
            current_question = $( "##{current_question.key}_field" )
            switch_question  = $( "##{switch_question_key}_field" )

            # Switch the highlighted tab on the left sidebar
            $( '.active' ).removeClass( 'active' )

            # Animate the switching
            current_question.fadeOut( 'fast', () ->
                switch_question.fadeIn( 'fast' ).addClass( 'active' )
                $( '.active input' ).focus()
            )

            @_display_form_buttons( question_index )

            @

        next_question: () ->

            question = @_active_question()
            question_index = question.idx

            # Attempt to switch to the next question
            if question_index < @input_fields.length
                question_index += 1

            @switch_question( $( '.control-group' ).eq( question_index )[0], true )

            @

        prev_question: () ->

            question = @_active_question()
            question_index = question.idx

            if question_index <= 0
                return @

            question_index -= 1
            @switch_question( $( '.control-group' ).eq( question_index )[0], false )

            @

    return xFormView
)
