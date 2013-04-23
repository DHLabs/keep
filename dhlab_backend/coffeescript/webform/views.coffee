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

        initialize: ->
            # Grab the form_id from the page
            @form_id  = $( '#form_id' ).html()
            @user     = $( '#user' ).html()

            # Begin render when the model is finished fetching from the server
            @listenTo( @model, 'change', @render )
            @model.fetch( { url: "/api/v1/repos/#{@form_id}/?user=#{@user}&format=json" } )

            @

        submit: ->
            posted_data = @renderedForm.getValue()
            console.log( posted_data )

            $.ajax(
                url: "/api/v1/repos/#{@form_id}/"
                data: posted_data
                type: "POST"
                success: () ->
                    window.location = '/'
            )

        recursiveAdd: build_form

        render: () ->
            #     groupBegin: '<div class="well"><div><strong>Group: </strong>{{title}}</div></div>'
            #     groupEnd: '<div><hr></div>'

            # Create the form to render
            _.each( @model.attributes.children, ( child ) =>
                @recursiveAdd( child )
            )

            # Create the Form object with the schema we want
            @renderedForm = new Backbone.Form(
                schema: @item_dict
                data:   @_data
                fields: @_fieldsets
            ).render()

            # Render it on the page!
            $('#formDiv').html( @renderedForm.el )

            # Create & render the html for the questions sidebar
            @_create_sidebar()

            $( '.control-group' ).first().show()

            @

        _create_sidebar: ->
            # Create sidebar
            if @input_fields.length == 0
                $( '#form_sidebar' ).html( '' )
                _.each( @item_dict, ( child, key ) =>

                    #if not child.is_field
                    #    return

                    element = "<li id='#{key}_tab' data-key='#{key}'"
                    if $( '#form_sidebar > li' ).length == 0
                        element += " class='active'"

                    if not XFormConstraintChecker.isRelevant( child, @renderedForm.getValue() )
                        element += " class='disabled'"
                    element += '>'

                    element += "<a href='#'>#{child.title}</a></li>"

                    child.name = key
                    @input_fields.push( child )

                    $( '#form_sidebar' ).append( element )
                )
            else
                _.each( @item_dict, ( child, key ) =>

                    #if not child.is_field
                    #    return

                    sidebar_element = $( "##{key}_tab" )
                    if not XFormConstraintChecker.isRelevant( child, @renderedForm.getValue() )
                        sidebar_element.addClass( 'disabled' )
                    else
                        sidebar_element.removeClass( 'disabled' )
                )

            @

        _display_form_buttons: ( question_index ) ->

            if question_index == 0
                $( '#prev_btn' ).hide()
                $( '#submit_btn' ).hide()

                $( '#next_btn' ).show()
            else if question_index == @input_fields.length - 1
                $( '#prev_btn' ).show()
                $( '#submit_btn' ).show()

                $( '#next_btn' ).hide()
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

        switch_question: ( element ) ->

            # Does the current active question pass our constraints?
            if not @passes_question_constraints()
                return @

            # Current question
            current_question = @_active_question()

            # Question to switch to
            switch_question_key = $( element.currentTarget ).data( 'key' )

            # Check constraints of this question before continuing
            question_index = -1
            form_info = _.find( @input_fields, ( child ) ->
                question_index += 1
                return child.name == switch_question_key
            )

            # Is this question relevant?
            if not XFormConstraintChecker.isRelevant( form_info, @renderedForm.getValue() )

                # Switch to the next question!
                if question_index < @input_fields.length
                    question_index += 1

                $( '#form_sidebar > li' ).eq( question_index ).trigger( 'click' )
                return

            # Find the next question to switch from and to.
            current_question = $( "##{current_question.key}_field" )
            switch_question  = $( "##{switch_question_key}_field" )

            # Switch the highlighted tab on the left sidebar
            $( '.active' ).removeClass( 'active' )
            $( "##{switch_question_key}_tab" ).addClass( 'active' )

            # Animate the switching
            current_question.fadeOut( 'fast', () ->
                switch_question.fadeIn( 'fast' )
            )

            @_display_form_buttons( question_index )
            @_create_sidebar()

            @

        next_question: () ->

            question = @_active_question()
            question_index = question.idx

            # Attempt to switch to the next question
            if question_index < @input_fields.length
                question_index += 1

            $( '#form_sidebar > li' ).eq( question_index ).trigger( 'click' )
            @

        prev_question: () ->

            question = @_active_question()
            question_index = question.idx

            if question_index <= 0
                return @

            question_index -= 1

            $( '#form_sidebar > li' ).eq( question_index ).trigger( 'click' )

            @

    return xFormView
)
