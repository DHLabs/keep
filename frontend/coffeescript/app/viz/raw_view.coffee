define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->


    class DataRawView extends DataTableView

        el: '#raw-viz'

        showView: ->
          ($ '#raw-viz').show()

        hideView: ->
          ($ '#raw-viz').hide()

        onRender: =>
          @$('.DataTable').addClass('DataTable--fitContainer')
          super

        initialize: () ->
            DataTableView::initialize.apply(@, arguments)

            # Load up the intial set of data to render.
            @collection.reset( document.initial_data )

    return DataRawView
)
