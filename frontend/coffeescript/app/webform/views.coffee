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
          @modalView = new LanguageSelectModal( { current: @current_language, view: this } )
          $('.modal').html( @modalView.render().el )
          @modalView.onAfterRender( $( '.modal' ) )
          @

        initialize: ->
            # Grab the form_id from the page
            @form_id  = $( '#form_id' ).html()
            @user     = $( '#user' ).html()

            @currentQuestionIndex = 0
            @numberOfQuestions = document.flat_fields.length

            @change_language @get_default_language()

            @repopulateForm()
            @show_first_question()
            @

        show_first_question: ->
          first_question = document.flat_fields[0]
          @toggle_question(first_question, false)
          @_display_form_buttons(0)


        change_language: (language) ->
          @current_language = language

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

        # return first key in dict, for example:
        # { 'English': 'cat', 'Spanish': 'gato' } => 'English'
        first_key: (dict) ->
          _.keys(dict)[0]


        # Returns the default language of the form.
        get_default_language: ->
          first_field = document.flat_fields[0]
          second_field = document.flat_fields[1]

          # The first field may be a tracker field, which is automatically
          # inserted (and thus doesn't have translations) in which case we
          # need to check the second field of the form.
          if not @get_translations(first_field)
            @get_translations(second_field)
          else
            @get_translations(first_field)

        # Defaults to English if an English label is present, otherwise returns
        # the first language it finds.
        get_translations: (field) ->
          if field.type is 'group'
            if typeof field.children[0].label is 'object'
              # Default to English, otherwise return first label found
              return 'English' if field.children[0].label['English']?
              return @first_key(field.children[0].label)
            else
              return field.children[0].label

          if field.type isnt 'group' and field.label?
            if typeof field.label is 'object'
              # Default to English, otherwise return first label found
              return 'English' if field.label['English']?
              return @first_key(field.label)
            else
              # doesn't have translations
              return null

        get_label: (dictionary) ->
          return '' if not dictionary.label?

          label = dictionary.label

          return label if typeof label is 'string'

          # otherwise label is a translation dict
          if label[@current_language]
            # has translation so return translated label
            return label[@current_language]
          else
            # has translations, but not the desired one so return first value.
            # for example:
            # { 'English': 'cat', 'Spanish': 'gato' } => 'cat'
            return label[@first_key(label)]

        submit: ->
            $( ".form" ).submit()

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
          return {} if url is ''

          # Slice off '?' if present
          qs = url or location.search
          qs = qs.slice(1) if qs[0] is '?'

          pair_strings = qs.split('&')
          result = {}
          for str in pair_strings
            [key, value] = str.split('=')
            result[key] = decodeURIComponent(value) or ''

          result

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

        _display_form_buttons: (question_index) ->
          # Last question
          if question_index >= @numberOfQuestions - 1
              $( '#prev_btn' ).show()
              $( '#submit_btn' ).show()
              $( '#next_btn' ).hide()

          # First question
          else if question_index is 0
              $( '#prev_btn' ).hide()
              $( '#submit_btn' ).hide()
              $( '#next_btn' ).show()

          # All other questions
          else
              $( '#prev_btn' ).show()
              $( '#next_btn' ).show()
              $( '#submit_btn' ).hide()

          # Always show submit button when editing an existing record
          $( '#submit_btn' ).show() if document.getElementById('detail_data_id') != null
          @

        passes_question_constraints: ->
          question = document.flat_fields[@currentQuestionIndex]

          # Check if the question is required and whether or not a value is
          # present. If not, raise an alert.
          if question.bind?.required is "yes"
            if @get_question_value(question).length is 0
              alert "Answer is required."
              return false

          # Ensure that the question passes any constraints, if given. If
          # not, raise an alert.
          if not XFormConstraintChecker.passesConstraint( question, @get_question_value(question) )
            alert "Answer doesn't pass constraint: #{question.info.bind.constraint}"
            return false

          return true

        get_question_value: ( question ) ->
          answers = $( ".form" ).serialize()
          answer_json = @queryStringToJSON(answers)

          if answer_json[question.name]?
            answer_json[question.name]
          else
            ""

        show_question: (question) ->
          @toggle_question(question, false)

        hide_question: (question) ->
          @toggle_question(question, true)

        toggle_question: (question, hide) ->
          return false if not question

          if hide
            $('#' + question.name + '_field').hide()
          else
            $('#' + question.name + '_field').show()

          # Hide/show all children in a group
          if question.type is 'group'
            for child in question.children
              @toggle_question( child, hide )

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

        switch_question: ( next_index, advancing ) ->
          #TODO: if in group, test relevance/constraint for all children
          current_question = document.flat_fields[@currentQuestionIndex]
          next_question = document.flat_fields[next_index]

          # Case 1: moving backwards through the form to the first question
          # ---------------------------------------------------------------
          #
          # Show the first question, and hide the 'Previous' button.
          if next_index is 0
            @hide_question current_question
            @show_question next_question
            @currentQuestionIndex = 0
            @update_progress_bar(0)
            @_display_form_buttons(0)
            return

          # Case 2: finished the last question in the form
          # ----------------------------------------------
          #
          # Show the submit button.
          if next_index >= @numberOfQuestions
            return unless @passes_question_constraints()
            @currentQuestionIndex = @numberOfQuestions
            @update_progress_bar(next_index)
            @_display_form_buttons(next_index)
            return

          # Case 3: general case, navigating forwards or backwards
          # ------------------------------------------------------

          # If the current question is a group, we must advance the index to
          # the end of the group to reach the next field.
          if advancing
            # Does the current question pass our constraints?
            return unless @passes_question_constraints()

            if current_question.type is 'group'
              next_index = next_index + current_question.children.length
              next_question = document.flat_fields[next_index]

              # If the last question is part of a group, then just show the submit button.
              if next_index >= @numberOfQuestions
                @update_progress_bar(next_index)
                @_display_form_buttons(next_index)
                return


          # If going backwards, check if the question is in a group. If the
          # next question is in a group, i.e. at the end of the group, then we
          # need to move the index back to the beginning of the group.
          else
            group = @get_group_for_question(next_question)
            if group
              next_index = next_index - group.children.length
              next_question = document.flat_fields[next_index]

          # Now that we've found the next question, we need to determine if
          # it's relevant; it could be irrelevant based on preceding values, or
          # a calculation.
          if (next_question.bind?.calculate?) or not
            XFormConstraintChecker.isRelevant( next_question, @queryStringToJSON( $( ".form" ).serialize()) )

              # If its a calculation, calculate it!
              $("#" + next_question.name).val _performCalcluate(next_question.bind.calculate)  if next_question.bind?.calculate?

              # Switch to the next question!
              if advancing
                next_index += 1 if next_index < @numberOfQuestions
              else
                next_index -= 1 if next_index > 0

              @switch_question( next_index, advancing )
              return

          # We've found the next question, so hide the current question, show
          # the next one, and update the controls.
          @hide_question current_question
          @show_question next_question
          @currentQuestionIndex = next_index
          @update_progress_bar(next_index)
          @_display_form_buttons(@currentQuestionIndex)

          #Start the Geopoint display if geopoint
          #_geopointDisplay()  if form_info.bind isnt `undefined` and form_info.bind.map isnt `undefined`

          @

        update_progress_bar: (next_index) ->
          new_width_percentage = ((next_index / @numberOfQuestions) * 100).toString()
          @$('.progress-bar').width("#{new_width_percentage}%")

        next_question: ->
          @switch_question( @currentQuestionIndex + 1, true )
          @

        prev_question: () ->
            @switch_question( @currentQuestionIndex - 1, false )
            @

    return xFormView
)
