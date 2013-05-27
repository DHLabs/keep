define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min' ],

( $, _, Backbone ) ->

    class RawView extends Backbone.View

        name: 'RawView'
        el: $( '#raw' )

        initialize: ( options ) ->
            @parent = options.parent
            @raw_headers = options.raw_headers
            @data = options.data

            @render()

        render: ->

            $( '#raw' ).html( '' )

            html = '<table id="raw_table" class="table table-striped table-bordered">'

            html += '<thead><tr>'
            headers = ''
            for key in @raw_headers
                html += "<th>#{key}</th>"
            html += '</tr></thead>'

            # Render the actual data
            html += '<tbody>'
            for datum in @data.models
                html += '<tr>'
                for key in @raw_headers

                    value = datum.get( 'data' )[ key ]

                    if value
                        html += "<td>#{value}</td>"
                    else
                        html += "<td>N/A</td>"

                html += '</tr>'

            html += '</tbody></table>'


            $( '#raw' ).html( html )

            # Render the table using jQuery's DataTable
            #
            # NOTE: Elements taken from DataTables blog post about using DT with
            # Bootstrap, http://www.datatables.net/blog/Twitter_Bootstrap_2
            #
            $( '#raw_table' ).dataTable(
                'sDom': "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>"
                'sPaginationType': 'bootstrap'
            )

            $.extend( $.fn.dataTableExt.oStdClasses, {
                "sWrapper": "dataTables_wrapper form-inline"
            } )

            @

    return RawView
)