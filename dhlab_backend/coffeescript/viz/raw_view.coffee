define( [ 'jquery',
          'vendor/underscore',
          'vendor/backbone-min',
          'masonry' ],

( $, _, Backbone, Masonry ) ->

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

            media_html = "<div id='media-container'>"

            html = '''
                    <div style='margin-bottom:16px;'>
                        <a><i class='icon-align-justify'></i>&nbsp;List View</a>
                        <a><i class='icon-th-large'></i>&nbsp;Grid View</a>
                    </div>
                    <table id="raw_table" class="table table-striped table-bordered">'''

            html += '<thead><tr>'
            headers = ''
            for field in @raw_headers
                html += "<th>#{field.name}</th>"
            html += '</tr></thead>'

            # Render the actual data
            html += '<tbody>'
            for datum in @data.models
                html += '<tr>'
                for field in @raw_headers

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