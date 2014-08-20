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
          'app/webform/constraints',
          'app/webform/modals/language' ],

( $, _, Backbone, Forms, L, xFormModel, XFormConstraintChecker, LanguageSelectModal ) ->

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
            'click #language-select-btn':'language_select'

        # languages:  []

        language_select: ( event ) ->
          @modalView = new LanguageSelectModal( { current: @currentLanguage, view: this } )
          $('.modal').html( @modalView.render().el )
          @modalView.onAfterRender( $( '.modal' ) )
          @

        initialize: ->
            # Grab the form_id from the page
            @form_id  = $( '#form_id' ).html()
            @user     = $( '#user' ).html()

            @currentQuestionIndex = 0
            @numberOfQuestions = document.flat_fields.length

            @currentLanguage = null
            if typeof(document.flat_fields[0].label) != "string"
              @currentLanguage = _.keys(document.flat_fields[0].label)[0]
              
            @repopulateForm()
            @_display_form_buttons( 0, document.flat_fields[0] )

            $(document).tooltip({
              content: () ->
                return $(this).prop('title')
                })
            @

        change_language: (language) ->
          @currentLanguage = language

          #iterate through all the questions and switch the text
          for question in document.flat_fields
            #set the label
            $('label[for="'+question.name+'"]').html( @get_label(question) )

            #change choice labels for select types
            if question.type.indexOf('select') > -1
              if question.bind and question.bind.appearance and question.bind.appearance == 'dropdown'
                for choice in question.choices
                  $("option[value='"+choice.name+"']").html( @get_label(choice) )
              else
                index = 0
                for choice in question.choices
                  $("label[for='"+question.name+"-"+index+"']").html( @get_label(choice) )
                  index++

          @

        get_label: (dictionary) ->
          if typeof dictionary == 'string'
            return dictionary.label
          else
            if @currentLanguage
              if dictionary.label[@currentLanguage]
                return dictionary.label[@currentLanguage]
              else
                return dictionary
            else
              #just return first string if no map for language
              return _.values(dictonary)[0]

        submit: ->
            $( ".form" ).submit()

        render: () ->
            # Creates submission page, takes care of corner case
            # submitChild =
            #   bind:
            #     readonly: "true()"          
            
            # if (@input_fields[0].bind and @input_fields[0].bind.group_start) or (@input_fields[0].control and @input_fields[0].control.appearance)
            #   _groupOperations.apply(@, [0, true])
            # else 
            #   $( '.control-group' ).first().show().addClass( 'active' )
            #   $( '.active input' ).focus()

            @_display_form_buttons( 0, null )

            # Render additional Geopoint if first question is one
            # _geopointDisplay()  if @_active_question().info.bind and @_active_question().info.bind.map
            @

        # _geopointDisplay = ->
        #   onMapClick = (e) ->
        #     popup.setLatLng(e.latlng).setContent("Latitude and Longitude: " + e.latlng.toString()).openOn map
        #     $("#" + question).val e.latlng.lat + " " + e.latlng.lng + " 0 0"
        #   map = undefined
        #   question = ($(".active").data("key"))
        #   element = document.getElementById(question + "_map")
        #   unless element.classList.contains("map")
        #     element.classList.add "map"
        #     map = L.map((question + "_map"),
        #       center: [36.60, -120.65]
        #       zoom: 5
        #     )
        #     L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png",
        #       attribution: "&copy; <a href=\"http://osm.org/copyright\">OpenStreetMap</a> contributors"
        #       maxZoom: 18
        #       reuseTiles: true
        #     ).addTo map
        #   popup = L.popup()
        #   map.on "click", onMapClick
        #   map.invalidateSize false

        queryStringToJSON: (url) ->
          if (url == '')
            return ''
          pairs = (url or location.search).slice(1).split('&')
          result = {}
          for idx in pairs
              pair = idx.split('=')
              if !!pair[0]
                  result[pair[0].toLowerCase()] = decodeURIComponent(pair[1] or '')
          
          return result

        replaceAll: (find, replace, str) ->
          return str.replace(new RegExp(find, 'g'), replace)

        repop_multiple: (newstring,object) ->
          cont = newstring
          while true
            index = cont.indexOf(object.name);
            if index == -1
                break
            cont = cont.substring(index, cont.length);
            andindex = cont.indexOf("&");
            value = cont.substring(object.name.length+1,andindex)
            cont = cont.substring( object.name.length+1, cont.length )
            $('input[value="' + value + '"]').prop('checked', true)

          @

        repopulateForm: ->
          #contents = document.getElementById('session-data').innerHTML;
          #contents = "?" + contents.trim();
          #contents = replaceAll('&amp;','&', contents);
          result = @queryStringToJSON(null)

          for  i in [0..(document.flat_fields.length-1)]
            obj = document.flat_fields[i]

            if obj.type == "group"
              for j in [0..(obj.children.length-1)]  
                obj2 = obj.children[j]
                if obj2.type == 'select all that apply' 
                  @repop_multiple(location.search,obj2)
                else if obj2.type == "select one"
                  $('input[value="' + result[obj2.name] + '"]').prop('checked', true)
                #else if( obj2.type == "geopoint" )
                #    handlegeopoint( result[obj2.name] )
                else
                  $('#'+obj2.name).val( result[obj2.name] )
            else 
              if obj.type == 'select all that apply'
                @repop_multiple(location.search,obj)
              else if obj.type == "select one"
                $('input[value="' + result[obj.name] + '"]').prop('checked', true)
              #else if obj.type == "geopoint"
              #handlegeopoint( result[obj.name] )
              else
                $('#'+obj.name).val( result[obj.name] )
          @

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
            if @input_fields[question].control.appearance is "field-list"
              current_tree = @input_fields[question].tree

              $('#' + @input_fields[question].name + '_field')
                .fadeIn(1)
                .addClass('active')
              question++
              question_info = @input_fields[question]

              while question_info.tree is current_tree
                question_change = $('#' + question_info.name + "_field")
                question_change.fadeIn(1).addClass('active')
                $('.active input').focus()
                question++
                question_info = @input_fields[question]

            # Grid-list controls (Not already a grid list)
            else if @input_fields[question].control.appearance is "grid-list" and !($('#' + @input_fields[question].name + '_field').hasClass('grid-list'))
              current_tree = @input_fields[question].tree

              # Create the table/grid (as divs)!
              table_name = @input_fields[question].name + '_table'
              $('#' + @input_fields[question].name + '_field')
                .fadeIn(1)
                .append($('<table id="' + table_name + '" class="grid-list"></div>'))
                .addClass('active grid-list')

              question++
              question_info = @input_fields[question]

              grid_row = 0
              # Add the First row to the table, first add blank cell
              $('#' + table_name).append('<tr id="' + table_name + '-' + grid_row + '" class="grid-list-row"></td>')
              $('#' + table_name + '-' + grid_row).append('<td />')
              for element, idx in question_info.options
                $('#' + table_name + '-' + grid_row).append('<td id="' + table_name + '-' + grid_row + '-' + idx +
                                                            '" class="grid-list-cell">' + element.label + '</td>')

              while question_info.tree is current_tree
                grid_row+=1

                # Remove the HTML of the old question
                $('#' + question_info.name + "_field").remove()

                question_change = question_info.name + '_field'

                # Create new row
                $('#' + table_name + ' tbody')
                  .append('<tr id ="' + question_change + '" data-key="' + question_info.name + '" class="active grid-list-row">')

                # Create label cell
                $('#' + question_change )
                  .append('<td class="grid-list-cell grid-list-label">
                            <label class="control-label" for="' + question_info.name + '"> ' + question_info.title + '</label></td>')

                # Create Radio cells
                for element, index in question_info.options
                  $('#' + question_change)
                    .append('<td class="grid-list-cell">
                              <input value="' + element.label + '" type="radio" name="' + question_info.name + '" id="' + question_info.name + '-' + index + '">
                            </td>')

                $('.active input').focus()
                question++
                question_info = @input_fields[question]

            # Grid-List controls (already processed to a grid-list)
            else if $('#' + @input_fields[question].name + '_field').hasClass('grid-list')
              question_change = '#' + @input_fields[question].name + "_field"
              $(question_change).fadeIn(1).addClass('active')
              $(question_change + ' tr').each( () ->
                $(@).fadeIn(1).addClass('active')
              )

          # Assumption of a group without controls
          else
            while @input_fields[question].bind and @input_fields[question].bind.group_start
              if forward
                if question < @input_fields.length
                  question++
              else
                if question > 0
                  question++
            question_change = $('#' + $($('.control-group').eq(question)[0]).data('key') + "_field")
            question_change.fadeIn(1).addClass('active')

          @

        _display_form_buttons: ( question_index, question ) ->

            if question_index == @numberOfQuestions - 1 or (not question)
                $( '#prev_btn' ).show()
                $( '#submit_btn' ).show()

                $( '#next_btn' ).hide()
                # $("html").keydown (e) ->
                #     $("#submit_btn").click()  if e.keyCode is 13

            else if question_index == 0
                $( '#prev_btn' ).hide()
                $( '#submit_btn' ).hide()

                $( '#next_btn' ).show()
                # $("#xform_view").keydown (e) ->
                #     $("#next_btn").click()  if e.keyCode is 13
            else
                $( '#prev_btn' ).show()
                $( '#next_btn' ).show()

                $( '#submit_btn' ).hide()
                # $("#xform_view").keydown (e) ->
                #     $("#next_btn").click()  if e.keyCode is 13

            if @currentQuestionIndex == 0
              $( '#prev_btn' ).hide()

            if document.getElementById( 'detail_data_id' ) != null
                $( '#submit_btn' ).show()
            @

        passes_question_constraints: ->
            #TODO: First check constraints on the question we're on
            question = document.flat_fields[@currentQuestionIndex]

            # Pass required?
            # if question.bind and question.bind.required is "yes"
            #     if @renderedForm.getValue()[ question.key ].length == 0
            #         $("#alert-placeholder").html "<div class=\"alert alert-error\"><a class=\"close\" data-dismiss=\"alert\">x</a><span>Answer is required.</span></div>"
            #         return false

            # Pass contraints?
            # if not XFormConstraintChecker.passesConstraint( question, @renderedForm.getValue() )
            #     $("#alert-placeholder").html "<div class=\"alert alert-error\"><a class=\"close\" data-dismiss=\"alert\">x</a><span>Answer doesn't pass constraint:" + question.info.bind.constraint + "</span></div>"
            #     return false

            return true

        get_question_value: ( question ) ->

          answers = $( ".form" ).serialize()
          answerJson = @queryStringToJSON(answers)

          return answerJson[question.name]

        toggle_question: (question, isHide) ->

          if not question
            return false

          if isHide
            $('#' + question.name + '_field').hide()
          else
            $('#' + question.name + '_field').show()

          if question.type == 'group'
            for i in [0..(question.children.length-1)]
              child = question.children[i]
              @toggle_question( child, isHide )

          return true

        get_group_for_question: (question, fields=document.flat_fields, group=null) ->

          for field in fields
            if field.type == 'group'
              thegroup = @get_group_for_question( question, field.children, field )
              if thegroup
                return thegroup
            else if field.name == question.name and group
              return group

          return null
    
        switch_question: ( next_index, forward ) ->

            #TODO: if in group, test relevance/constraint for all children

            # Does the current active question pass our constraints?
            if forward
                if not @passes_question_constraints()
                    return @

            previous_question = document.flat_fields[@currentQuestionIndex]
            if not previous_question
              @_display_form_buttons( @currentQuestionIndex, current_question )
              return

            if previous_question.type == 'group' and next_index != -1
              #TODO: check if group is field-list or not first
              if forward
                next_index = next_index + previous_question.children.length
            
            # Question to switch to
            #switch_question_key = $( element ).data( 'key' )

            # Check constraints of this question before continuing
            #question_index = -1
            # form_info = _.find( @input_fields, ( child ) ->
            #     @currentQuestionIndex += 1
            #     return child.name == switch_question_key
            # )
            current_question = document.flat_fields[next_index]
            if not forward
              #is current question within group
              group = @get_group_for_question(current_question)
              if group
                next_index = next_index - group.children.length
                current_question = document.flat_fields[next_index]

            if not current_question
              @_display_form_buttons( @currentQuestionIndex, current_question )
              return

            #Is this question relevant?  Or, is this question an equation?
            if (current_question.bind and current_question.bind.calculate != null) or current_question.type == 'calculate' or not 
              XFormConstraintChecker.isRelevant( current_question, @queryStringToJSON($( ".form" ).serialize()) )
                # If its a calculation, calculate it!
                $("#" + current_question.name).val _performCalcluate(current_question.bind.calculate)  if current_question.bind and current_question.bind.calculate

                # Switch to the next question!
                if forward
                    if next_index < @numberOfQuestions
                        next_index += 1
                else
                    if next_index > 0
                        next_index -= 1

                @switch_question( next_index, forward )
                return

            if @toggle_question(current_question, false)
              @toggle_question(previous_question, true)
            
            # If there is a query to a previous answer, display that answer
            # subsequent = undefined
            # if (form_info.title and subsequent = form_info.title.indexOf("${")) isnt -1
            #   end_subsequent = form_info.title.indexOf("}", subsequent)
            #   subsequent_st = form_info.title.substring(subsequent + 2, end_subsequent)
            #   switch_question[0].innerHTML = switch_question[0].innerHTML.replace(/\${.+}/, $("#" + subsequent_st).val())

            @currentQuestionIndex = next_index
            #Start the Geopoint display if geopoint
            #_geopointDisplay()  if form_info.bind isnt `undefined` and form_info.bind.map isnt `undefined`

            @_display_form_buttons( @currentQuestionIndex, current_question )

            @

        next_question: () ->

            #currentQuestion = document.repo.children[@currentQuestionIndex]

            # Set up for field lists and grid lists
            # if question.info.control and question.info.control.appearance
            #     current_tree = question.info.tree
            #     question_index += 1
            #     question_index += 1  while @input_fields[question_index].tree is current_tree 

            # Attempt to switch to the next question
            #if question_index < @input_fields.length
            #    question_index += 1

            @switch_question( @currentQuestionIndex + 1, true )

            @

        prev_question: () ->

            # question = @_active_question()

            # if question_index <= 0
            #     return @

            # current_tree = @input_fields[question_index - 1].tree

            # # If we are in a group, check if we are in a field/grid list group
            # unless current_tree is "/"
            #   temp_idx = question_index - 1
            #   temp_idx -= 1  while temp_idx >= 0 and @input_fields[temp_idx].tree is current_tree
            #   temp_idx += 1
            #   if @input_fields[temp_idx].control and @input_fields[temp_idx].control.appearance
            #     question_index = temp_idx
            #   else
            #     question_index -= 1
            # else
            #   question_index -= 1
              
            @switch_question( @currentQuestionIndex - 1, false )

            @

    return xFormView
)
