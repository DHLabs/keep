define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

  class DataRawView extends DataTableView
      el: '#raw-viz'

      onRender: =>
        @$('.DataTable').addClass('DataTable--fitContainer')
        super

      onShow: -> @delegateEvents()

      # Load up the intial set of data to render.
      initialize: (options) ->
        super
        @collection.reset(document.initial_data)

  return DataRawView
)
