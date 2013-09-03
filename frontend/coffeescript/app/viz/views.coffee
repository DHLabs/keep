define( [ 'jquery',
          'underscore',
          'backbone',
          'marionette',

          'app/models/data',
          'app/models/repo',
          'app/collections/data' ],

( $, _, Backbone, Marionette, DataModel, RepoModel, DataCollection ) ->

    class RawItemView extends Backbone.Marionette.ItemView
        tagName: 'tr'

        initialize: (options) ->
            @fields = options.fields

        template: ( model ) =>
            data = { fields: @fields, model: model }

            templ = _.template( '''
                <% _.each( fields, function( field ) { %>
                    <td><%= model.data[ field.name ] %></td>
                <% }); %>''')

            return templ( data )


    class RawView extends Backbone.Marionette.CollectionView
        el: '#raw-viz table'
        itemView: RawItemView
        collection: new DataCollection

        header_template: _.template( '''
                <tr>
                <% _.each( fields, function( item ) { %>
                    <th><%= item.name %></th>
                <% }); %>
                </tr>
            ''')

        initialize: ( options )->
            @fields = options.fields
            @$el.append( @header_template( options ) )
            @

        buildItemView: ( item, ItemViewType, itemViewOptions ) ->
            options = _.extend( { model: item, fields: @fields }, itemViewOptions )
            return new ItemViewType( options )


    class VizChrome extends Backbone.Marionette.Region
        el: '#viz-chrome'


    class VizData extends Backbone.Marionette.Region
        el: '#viz-data'

        initialize: ( options ) ->

            @rawView = new RawView( options )
            @rawView.collection.reset( document.initial_data )
            @attachView( @rawView )

    # Instantiate and startup the new process.
    DataVizView = new Backbone.Marionette.Application

    DataVizView.addInitializer ( options ) ->

        @repo = new RepoModel( document.repo )

        # Add the different regions
        vizChrome = new VizChrome
        vizData   = new VizData( { fields: @repo.fields() } )

        DataVizView.addRegions(
                chrome: vizChrome
                viz: vizData )
        @

    return DataVizView
)

remove_permissions= (div,username) ->
    $.ajax({
        type: "DELETE",
        url: "/repo/user_share/"+$( '#form_id' ).html()+"/?username=" + username,
        data: "username=" + username,
        success: () ->
            div.parentNode.parentNode.innerHTML = ""

    })
    @
