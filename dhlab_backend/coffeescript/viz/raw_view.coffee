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
            "click .btn-group > button":    "change_viz_type"
            "change #test":                 "toggle_media"

        media_base: '//d2oeqvnrcsteq9.cloudfront.net/'

        column_headers: []
        groups: []

        card_tmpl: _.template( '''
            <div class='card card-active'>
                <%= card_image %>
                <%= card_data %>
            </div>''' )

        card_img_tmpl: _.template( '''
            <div class='card-image'>
                <a href='<%= url %>' target='_blank'>
                    <img src='<%= url %>'>
                </a>
            </div>''' )

        card_video_tmpl: _.template( '''
            <div class='card-video'>
                <video controls>
                    <source src='<%= url %>' type='video/mp4; codecs="avc1.42E01E, mp4a.40.2"' />
                </video>
            </div>''' )

        card_data_tmpl: _.template( '''
            <div class='card-data'>
                <div><%= data %></div>
            </div>''' )

        _detect_headers: ( root ) ->

            for field in root
                if field.type in [ 'group' ]
                    @_detect_headers( field.children )

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

                if viz_type == 'grid' and @wall?
                    @wall.masonry( 'reload' )
            )

        toggle_media: ( event ) ->
            only_photos = $( event.currentTarget ).is( ':checked' )

            $( '.card' ).each( ()->
                if $( '.card-image', @ ).length == 0 and only_photos
                   $( @ ).fadeOut( 'fast' ).removeClass( 'card-active' )
                else
                    $( @ ).fadeIn( 'fast' ).addClass( 'card-active' )
            )

            @wall.masonry( 'reload' )

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

                    console.log( field )

                    if field.type in [ 'photo', 'video' ]
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
                    card_image: ''
                    card_data: ''

                for field in @column_headers
                    value = datum.get( 'data' )[ field.name ]

                    if not value? or value.length == 0
                        continue

                    if field.type in [ 'photo' ]
                        url = @media_base + "#{datum.get('repo')}/#{datum.get('_id')}/#{value}"
                        tmpl_options.card_image = @card_img_tmpl( { url: url } )
                    else if field.type in [ 'video' ]
                        url = @media_base + "#{datum.get('repo')}/#{datum.get('_id')}/#{value}"
                        tmpl_options.card_image = @card_video_tmpl( { url: url } )
                    else
                        tmpl_options.card_data += "<div><strong>#{field.name}:</strong> #{value}</div>"

                if tmpl_options.card_data.length > 0
                    tmpl_options.card_data = @card_data_tmpl( { data: tmpl_options.card_data } )

                $( '#raw_grid' ).append( @card_tmpl( tmpl_options ) )

                @wall = $( '#raw_grid' ).masonry(
                        itemSelector: '.card-active'
                        isAnimated: true )

            @

        render: ->
            @_render_list()

            if @data.models.length > 0
                @_render_grid()

            @

    return RawView
)