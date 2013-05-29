define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'masonry' ],

( $, _, Backbone, Masonry ) ->

    class RawView extends Backbone.View

        name: 'RawView'
        el: $( '#raw_viz' )
        events:
            # Change raw viz type from list to grid view
            "click .btn-group > button":     "change_viz_type"

        media_base: '//d2oeqvnrcsteq9.cloudfront.net/'

        column_headers: [ {'name': 'uuid', 'type': 'text'} ]

        card_tmpl: _.template( '''
            <div class='card'>
                <div class='card-image'>
                    <img src='<%= card_image %>'>
                </div>
                <div class='card-data'>
                    <div><%= card_data %></div>
                </div>
            </div>''' )

        _detect_headers: ( root ) ->

            for field in root
                if field.type in [ 'group' ]
                    @_detect_types( field.children )

                # Don't show notes in the raw data table
                if field.type not in [ 'note' ]
                    @column_headers.push( field )

        initialize: ( options ) ->
            @parent = options.parent
            @form   = options.form
            @data   = options.data

            @_detect_headers( @form.attributes.children )

            @render()

        change_viz_type: ( event ) ->
            viz_type = $( event.currentTarget ).data( 'type' )
            $( 'button.active', @el ).removeClass( 'active' )
            $( event.currentTarget ).addClass( 'active' )

            $( 'div.active').fadeOut( 'fast', () =>
                $( 'div.active' ).removeClass( 'active' )
                $( "#raw_#{viz_type}" ).fadeIn( 'fast' ).addClass( 'active' )

                if viz_type == 'grid'
                    $( '#raw_grid' ).masonry(
                        itemSelector: '.card' )
            )

        _render_list: ->
            # Add column headers
            $( '#raw_table > thead > tr' ).html( '' )
            for field in @column_headers
                $( '#raw_table > thead > tr' ).append( "<th>#{field.name}</th>" )

            # Add data from data models
            for datum in @data.models
                row_html = '<tr>'
                for field in @column_headers

                    value = datum.get( 'data' )[ field.name ]

                    if not value?
                        row_html += '<td>&nbsp;</td>'
                        continue

                    if field.type in [ 'photo' ]
                        url = @media_base + "#{datum.get('repo')}/#{datum.get('_id')}/#{value}"
                        row_html += "<td><a href='#{url}'>#{value}</a></td>"
                    else
                        row_html += "<td>#{value}</td>"

                row_html += '</tr>'

                $( '#raw_table > tbody' ).append( row_html )

            # Render the table using jQuery's DataTable
            #
            # NOTE: Elements taken from DataTables blog post about using DT with
            # Bootstrap, http://www.datatables.net/blog/Twitter_Bootstrap_2
            #
            $( '#raw_table' ).dataTable(
                'sDom': "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>"
                'sPaginationType': 'bootstrap'
                'bLengthChange': false
                'bFilter': false
                'iDisplayLength': 25
            )

            $.extend( $.fn.dataTableExt.oStdClasses, {
                "sWrapper": "dataTables_wrapper form-inline"
            } )

        _render_grid: ->
            # Add data from data models
            for datum in @data.models

                tmpl_options =
                    card_image: '//placehold.it/220x100'
                    card_data: ''

                for field in @column_headers
                    value = datum.get( 'data' )[ field.name ]
                    if not value?
                        value = ''

                    if field.type in [ 'photo' ] and value.length > 0
                        url = @media_base + "#{datum.get('repo')}/#{datum.get('_id')}/#{value}"
                        tmpl_options.card_image = url
                    else
                        tmpl_options.card_data += "<div><strong>#{field.name}:</strong> #{value}</div>"


                $( '#raw_grid' ).append( @card_tmpl( tmpl_options ) )

            @

        render: ->
            @_render_list()
            @_render_grid()

            @

    return RawView
)