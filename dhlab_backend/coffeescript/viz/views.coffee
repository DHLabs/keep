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
            "click #viz_options a":         "switch_viz"
            "change #sharing_toggle":       "toggle_public"

        # Current list of survey data
        data: new DataCollection()

        # Current form that this data was for
        form: new FormModel()

        subviews: []

        initialize: ->
            # Begin render when the list is finished syncing with the server
            @listenTo( @form, 'sync', @render )
            @form.fetch()

            @data = new DataCollection()
            @data.reset( document.initial_data )

            @

        add_subview: (View) ->
            options =
                parent: @
                data: @data
                form: @form

            subview = new View( options )
            @subviews.push( subview )

            return subview

        toggle_public: (event) ->
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

            # Make sure that this tab isn't disabled before trying to switch
            # to the view.
            if $( event.currentTarget.parentNode ).hasClass( 'disabled' )
                return false

            $( 'li.active' ).removeClass( 'active' )
            $( event.currentTarget.parentNode ).addClass( 'active' )

            $( '.viz-active' ).fadeOut( 'fast', ()->
                $( @ ).removeClass( 'viz-active' )

                $( '#' + viz_type + '_viz' ).fadeIn( 'fast', ()=>
                    # Remember to redraw the map when we switch tabs
                    if viz_type == 'map'
                        document.vizApp.map_view.map.invalidateSize( false )
                ).addClass( 'viz-active' )
            )

            # Prevent propagation of the event down the event chain.
            return false

        render: ->
            # Don't render until we get both the form & survey data
            if( !@form.attributes.children || !@data )
                return

            if @raw_view is undefined
                @raw_view = @add_subview( RawView )

            if @chart_view is undefined
                @chart_view = @add_subview( ChartView )

            if @map_view is undefined
                @map_view = @add_subview( MapView )

    return DataView
)
