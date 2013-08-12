# TODO
#   - Handle xform bindings
#       - Required
#       - Constraints
#       - etc
#
#
define( [ 'jquery',
          'underscore',
          'backbone',
          'backbone-forms',
          'leaflet',
          'app/webform/models',
          'app/webform/builder',
          'app/webform/constraints' ],

( $, _, Backbone, Forms, L, xFormModel, build_form, XFormConstraintChecker ) ->

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
                @recursiveAdd( child, "/", @model.attributes.default_language )
            )

            # Create the Form object with the schema we want
            @renderedForm = new Backbone.Form(
                schema: @item_dict
            ).render()

            _.each( @item_dict, ( child, key ) =>
                child.name = key
                @input_fields.push( child )
            )

            # Render it on the page!
            $('#formDiv').html( @renderedForm.el )

            if @input_fields[0].bind and @input_fields[0].bind.group_start
              _groupOperations.apply(@, [@input_fields[0], true])
            else 
              $( '.control-group' ).first().show().addClass( 'active' )
              $( '.active input' ).focus()

            @_display_form_buttons( 0 )

            # Render additional Geopoint if first question is one
            _geopointDisplay()  if @_active_question().info.bind and @_active_question().info.bind.map
            @

        _geopointDisplay = ->
          onMapClick = (e) ->
            popup.setLatLng(e.latlng).setContent("Latitude and Longitude: " + e.latlng.toString()).openOn map
            $("#" + question).val e.latlng.lat + " " + e.latlng.lng + " 0 0"
          map = undefined
          question = ($(".active").data("key"))
          element = document.getElementById(question + "_map")
          unless element.classList.contains("map")
            element.classList.add "map"
            map = L.map((question + "_map"),
              center: [36.60, -120.65]
              zoom: 5
            )
            L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png",
              attribution: "&copy; <a href=\"http://osm.org/copyright\">OpenStreetMap</a> contributors"
              maxZoom: 18
              reuseTiles: true
            ).addTo map
          popup = L.popup()
          map.on "click", onMapClick
          map.invalidateSize false

        # For calculations.  Currently only supporting basic -, +, *, div
        _performCalcluate = (equation) ->
          evaluation = undefined
          i = undefined
          begin = undefined
          end = undefined
          side1 = undefined
          side2 = undefined
          operation = undefined
          parenCount = undefined
          parenCount = 0
          
          # Initial paren finder and recursion to get to the start of the equation
          i = 0
          while i < equation.length
            if equation[i] is "("
              begin = i  if parenCount is 0
              parenCount++
            else if equation[i] is ")"
              parenCount--
              if parenCount is 0
                end = i
                equation = equation.replace(equation.substring(begin, end + 1), _performCalcluate(equation.substring(begin + 1, end)))
            i++
          side1 = equation.slice(0, equation.indexOf(" "))
          operation = equation.slice(side1.length + 1, equation.lastIndexOf(" "))
          side2 = equation.slice(equation.lastIndexOf(" ") + 1)
          side1 = $("#" + side1.slice(2, -1)).val()  if side1.slice(0, 2) is "${"
          side2 = $("#" + side2.slice(2, -1)).val()  if side2.slice(0, 2) is "${"
          console.log side1 + ", " + operation + ", " + side2
          if operation is "-"
            return (side1 - side2)
          else if operation is "+"
            return (side1 + side2)
          else if operation is "*"
            return (side1 * side2)
          else if operation is "div"
            return (side1 / side2)
          else
            return

        # Group Operations moved here, to hopefully better handle groups being a first question
        _groupOperations = (question, forward) ->
          # First, group controls
          if @input_fields[question].control

            # Field-list controls
            if @input_fields[question].control.appearance is "field-list" or (@input_fields[question].control.appearance is "grid-list" and $('#' + @input_fields[question].name + '_field').hasClass('grid-list'))
              current_tree = @input_fields[question].tree
              $('#' + @input_fields[question].name + '_field')
                .fadeIn(1)
                .addClass('active')
              question++
              question_info = @input_fields[question]

              while question_info.tree is current_tree
                switch_question = $('#' + $($('.control-group').eq(question)[0]).data('key') + "_field")
                switch_question.fadeIn(1).addClass('active')
                $('.active input').focus()
                question++
                question_info = @input_fields[question]

            # Grid-list controls
            else if @input_fields[question].control.appearance is "grid-list"
              current_tree = @input_fields[question].tree
              console.log(@input_fields[question])
              # Create the table/grid (as divs)!
              table_name = @input_fields[question].name + '_table'
              $('#' + @input_fields[question].name + '_field')
                .fadeIn(1)
                .append($('<div id="' + table_name + '" class="grid-list"></div>'))
                .addClass('active grid-list')

              question++
              question_info = @input_fields[question]

              grid_row = 0
              # Add the First row to the table
              $('#' + table_name).append('<div id="' + table_name + '-' + grid_row + '" class="grid-list-row"></div>')
              $('#' + question_info.name + ' option').each( (idx) ->
                $('#' + table_name + '-' + grid_row).append('<div id="' + table_name + '-' + grid_row + '-' + idx +
                                                            '" class="grid-list-cell">' + $(@)[0].innerHTML + '</div>')
              )

              while question_info.tree is current_tree
                grid_row+=1
                switch_question = $('#' + $($('.control-group').eq(question)[0]).data('key') + "_field")

                # First, change the select to a list, then change the options to radio buttons
                attrs = { }
                $.each($('#' + switch_question[0].id + ' select')[0].attributes, (idx, attr) ->
                  attrs[attr.nodeName] = attr.value
                )
                console.log(attrs)
                $('#' + switch_question[0].id + ' select').replaceWith( () ->
                  return $("<div />", attrs).append($(@).contents()) )

                $('#' + switch_question[0].id + ' option').each( (index) ->
                  attrs = { }
                  $.each($(@)[0].attributes, (idx, attr) ->
                    attrs[attr.nodeName] = attr.value
                  )
                  attrs.type = 'radio'
                  attrs.name = switch_question.data('key')
                  attrs.id = switch_question.data('key') + '-' + index
                  $(@).replaceWith( () ->
                    return $("<input />", attrs) ) #.append($(@).contents()) )
                  $('#' + attrs.id)
                    .appendTo($(switch_question))
                    .wrap('<div class="grid-list-cell" />')#.parent()
                  #$(@).appendTo($('#' + table_name)).wrap('<td></td>')
                )

                $('#' + switch_question[0].id + ' label').wrap('<div class="grid-list-cell" />')

                $('#' + switch_question[0].id + ' .controls').remove()#.attr('display', 'inline-block')

                # Then, move the question into the grid-list as a grid-row
                $(switch_question)
                  .appendTo($('#' + table_name))
                  .wrap('<div id="' + table_name + '-' + grid_row + '" class="grid-list-row" />')


                switch_question.fadeIn(1).addClass('active')
                $('.active input').focus()
                question++
                question_info = @input_fields[question]

          # Assumption of a group without controls
          else
            while @input_fields[question].bind and @input_fields[question].bind.group_start
              if forward
                if question < @input_fields.length
                  question++
              else
                if question > 0
                  question++
            switch_question = $('#' + $($('.control-group').eq(question)[0]).data('key') + "_field")
            switch_question.fadeIn(1).addClass('active')

          @



        _display_form_buttons: ( question_index ) ->

            if question_index == @input_fields.length - 1
                $( '#prev_btn' ).show()
                $( '#submit_btn' ).show()

                $( '#next_btn' ).hide()
                $("html").keydown (e) ->
                    $("#submit_btn").click()  if e.keyCode is 13

            else if question_index == 0
                $( '#prev_btn' ).hide()
                $( '#submit_btn' ).hide()

                $( '#next_btn' ).show()
                $("#xform_view").keydown (e) ->
                    $("#next_btn").click()  if e.keyCode is 13
            else
                $( '#prev_btn' ).show()
                $( '#next_btn' ).show()

                $( '#submit_btn' ).hide()
                $("#xform_view").keydown (e) ->
                    $("#next_btn").click()  if e.keyCode is 13
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
                    $("#alert-placeholder").html "<div class=\"alert alert-error\"><a class=\"close\" data-dismiss=\"alert\">x</a><span>Answer is required.</span></div>"
                    return false

            # Pass contraints?
            if not XFormConstraintChecker.passesConstraint( question.info, @renderedForm.getValue() )
                $("#alert-placeholder").html "<div class=\"alert alert-error\"><a class=\"close\" data-dismiss=\"alert\">x</a><span>Answer doesn't pass constraint:" + question.info.bind.constraint + "</span></div>"
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

            # Is this question relevant?  Or, is this question an equation?
            if (form_info.bind and form_info.bind.calculate) or not XFormConstraintChecker.isRelevant( form_info, @renderedForm.getValue() )
                # If its a calculation, calculate it!
                $("#" + form_info.name).val _performCalcluate(form_info.bind.calculate)  if form_info.bind and form_info.bind.calculate

                # Switch to the next question!
                if forward
                    if question_index < @input_fields.length
                        question_index += 1
                else
                    if question_index > 0
                        question_index -= 1

                @switch_question( $( '.control-group' ).eq( question_index ), forward )
                return

            # Animate and remove the current question and any possible alerts
            $(".active").fadeOut 1
            $(".alert").fadeOut 1
            $(".active").removeClass "active"

            if form_info.bind and form_info.bind.group_start
              _groupOperations.apply(@, [question_index, forward])

            else
              switch_question = $("#" + $($(".control-group").eq(question_index)[0]).data("key") + "_field")
              form_info = @input_fields[question_index]

              # If there is a query to a previous answer, display that answer
              subsequent = undefined
              if (form_info.title and subsequent = form_info.title.indexOf("${")) isnt -1
                end_subsequent = form_info.title.indexOf("}", subsequent)
                subsequent_st = form_info.title.substring(subsequent + 2, end_subsequent)
                switch_question[0].innerHTML = switch_question[0].innerHTML.replace(/\${.+}/, $("#" + subsequent_st).val())
          
              switch_question.fadeIn(1).addClass "active"
            
            #Start the Geopoint display if geopoint
            _geopointDisplay()  if form_info.bind isnt `undefined` and form_info.bind.map isnt `undefined`

            @_display_form_buttons( question_index )

            @

        next_question: () ->

            question = @_active_question()
            question_index = question.idx

            # Set up for field lists and grid lists
            if question.info.control and question.info.control.appearance
                current_tree = question.info.tree
                question_index += 1
                question_index += 1  while @input_fields[question_index].tree is current_tree 

            # Attempt to switch to the next question
            else if question_index < @input_fields.length
                question_index += 1

            @switch_question( $( '.control-group' ).eq( question_index )[0], true )

            @

        prev_question: () ->

            question = @_active_question()
            question_index = question.idx

            if question_index <= 0
                return @

            current_tree = @input_fields[question_index - 1].tree

            # If we are in a group, check if we are in a field/grid list group
            unless current_tree is "/"
              temp_idx = question_index - 1
              temp_idx -= 1  while temp_idx >= 0 and @input_fields[temp_idx].tree is current_tree
              temp_idx += 1
              if @input_fields[temp_idx].control and @input_fields[temp_idx].control.appearance
                question_index = temp_idx
              else
                question_index -= 1
            else
              question_index -= 1
              
            @switch_question( $( '.control-group' ).eq( question_index )[0], false )

            @

    return xFormView
)
