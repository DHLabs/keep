define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'vendor/forms/backbone-forms.min',
          'raw_view',
          'map_view',
          'chart_view' ],

( $, _, Backbone, Forms, RawView, MapView, ChartView ) ->

    class DataModel extends Backbone.Model
        defaults:
            data: []


    class FormModel extends Backbone.Model
        initialize: ->
            @form_id = $( '#form_id' ).html()
            @user    = $( '#user' ).html()

            @url = "/api/v1/repos/#{@form_id}/?format=json&user=#{@user}"


    class DataCollection extends Backbone.Collection
        model: DataModel

        initialize: ->
            # Grab the form_id from the page
            @form_id = $( '#form_id' ).html()
            @url = "/api/v1/data/#{@form_id}/?format=json"

        comparator: ( data ) ->
            return data.get( 'timestamp' )


    class DataView extends Backbone.View

        # The HTML element where the viz will be rendered
        el: $( '#viz' )

        events:
            "click #yaxis_options input":   "change_y_axis"
            "click #viz_options a":         "switch_viz"
            "change #sharing_toggle":       "toggle_public"

        # Current list of survey data
        data: new DataCollection()

        # Current form that this data was for
        form: new FormModel()

        subviews: []

        # Raw data stuff
        raw_headers: [ 'uuid' ] # Headers used for the raw data table header

        # Map related stuff
        map_headers: null       # Map related headers (geopoint datatype)
        map_enabled: false      # Did we detect any geopoints in the data?
        map: null               # Map object

        # Yaxis chosen by the user
        yaxis: null
        chart_fields: []

        # In pixels
        width:  750
        height: 250

        initialize: ->
            # Begin render when the list is finished syncing with the server
            @listenTo( @form, 'sync', @render )
            @form.fetch()

            @data = new DataCollection()
            @data.reset( document.initial_data )

            @

        toggle_public: (event) ->
            console.log( 'called' )

            $.post( "/repo/share/#{@form.form_id}/", {}, ( response ) =>
                if response.success
                    $( event.currentTarget ).attr( 'checked', response.public )

                    if response.public
                        $( '#privacy > div' ).html( '<i class=\'icon-unlock\'></i>&nbsp;PUBLIC' )
                    else
                        $( '#privacy > div' ).html( '<i class=\'icon-lock\'></i>&nbsp;PRIVATE' )
            )

            @

        switch_viz: (event) ->

            viz_type = $( event.currentTarget ).data( 'type' )

            # Check that the viz is enabled
            if viz_type == 'map' and not @map_enabled
                return
            else if viz_type == 'line' and @chart_fields.length == 0
                return

            $( '.active' ).removeClass( 'active' )
            $( event.currentTarget.parentNode ).addClass( 'active' )

            $( '.viz-active' ).fadeOut( 'fast', ()->
                $( @ ).removeClass( 'viz-active' )

                $( '#' + viz_type + '_viz' ).fadeIn( 'fast', ()=>
                    # Remember to redraw the map when we switch tabs
                    if viz_type == 'map'
                        document.vizApp.map_view.map.invalidateSize( false )
                ).addClass( 'viz-active' )
            )


        change_y_axis: (event) ->
            # Ensure everything else is unchecked
            $( '#yaxis_options input' ).attr( 'checked', false )
            $( event.target ).attr( 'checked', true )

            # Assign the yaxis
            @yaxis = event.target.value

            # Re-render chart
            @renderCharts()

        _detect_types: ( root ) ->
            for field in root
                if field.type in [ 'group' ]
                    @_detect_types( field.children )

                # Don't show notes in the raw data table
                if field.type not in [ 'note' ]
                    @raw_headers.push( field )

                # Only chart fields that are some sort of number
                if field.type in [ 'decimal', 'int', 'integer' ]

                    @chart_fields.push( field.name )

                    # If we haven't set a default Y-axis yet, set it!
                    if not @yaxis
                        @yaxis = field.name

                # Detect geopoints
                if field.type in [ 'geopoint' ]
                    # Enable the map button
                    $( '#map_btn' ).removeClass( 'disabled' )

                    @map_enabled = true
                    @map_headers = field.name

        render: ->
            # Don't render until we get both the form & survey data
            if( !@form.attributes.children || !@data )
                return

            # Loop through the form fields and check to see what type of visualizations
            # we can do.
            @_detect_types( @form.attributes.children )

            if @raw_view is undefined
                @raw_view = new RawView(
                                    parent: @
                                    raw_headers: @raw_headers
                                    data: @data )
                @subviews.push( @raw_view )

            if @chart_view is undefined
                @chart_view = new ChartView(
                                    parent: @
                                    chart_fields: @chart_fields
                                    data: @data )
                @subviews.push( @chart_view )

            if @map_view is undefined
                @map_view = new MapView(
                                    parent: @
                                    map_headers: @map_headers
                                    data: @data )
                @subviews.push( @chart_view )

            # Only render other vizs if we actually have data!
            if @data.models.length > 0
                # Can we render a map?
                if @map_enabled
                    @map_view.render()
                else
                    $( '#map' ).hide()

                # Can we render any charts?
                if @chart_fields.length
                    @chart_view.render()
                else
                    $( '#line_btn' ).addClass( 'disabled' )
            else
                # Disable all the data viz buttons if we have no data
                $( '#line_btn' ).addClass( 'disabled' )
                $( '#map_btn' ).addClass( 'disabled' )
            @

    return DataView
)
