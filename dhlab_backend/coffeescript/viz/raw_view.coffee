define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'masonry' ],

( $, _, Backbone, Masonry ) ->

    class RawView extends Backbone.View

        name: 'RawView'
        el: $( '#raw' )

        column_headers: [ {'name': 'uuid', 'type': 'text'} ]

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

        render: ->

            $( '#raw' ).html( '' )

            media_html = "<div id='media-container'>"

            html = '<table id="raw_table" class="table table-striped table-bordered">'

            html += '<thead><tr>'
            headers = ''

            for field in @column_headers
                html += "<th>#{field.name}</th>"
            html += '</tr></thead>'

            # Render the actual data
            html += '<tbody>'
            for datum in @data.models
                html += '<tr>'
                for field in @column_headers

                    value = datum.get( 'data' )[ field.name ]

                    if value
                        if field.type in [ 'photo' ]
                            url = "//s3.amazonaws.com/keep-media/#{datum.get('repo')}/#{datum.get('_id')}/#{value}"

                            html += "<td><a href='#{url}'>#{value}</a></td>"
                        else
                            html += "<td>#{value}</td>"
                    else
                        html += "<td>N/A</td>"

                html += '</tr>'

            html += '</tbody></table>'
            html += media_html + "</div>"

            $( '#raw' ).html( html )

            #wall = new Masonry( document.getElementById('media-container') );

            # Render the table using jQuery's DataTable
            #
            # NOTE: Elements taken from DataTables blog post about using DT with
            # Bootstrap, http://www.datatables.net/blog/Twitter_Bootstrap_2
            #
            oTable = $( '#raw_table' ).dataTable(
                'sDom': "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>"
                'sPaginationType': 'bootstrap'
                'bLengthChange': false
                'bFilter': false
            )

            $.extend( $.fn.dataTableExt.oStdClasses, {
                "sWrapper": "dataTables_wrapper form-inline"
            } )

            new FixedColumns( oTable )

            @

    return RawView
)