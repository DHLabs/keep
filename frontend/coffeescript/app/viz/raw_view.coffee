define( [ 'jquery',
          'underscore',
          'backbone'
          'marionette',

          'app/collections/views/table' ],

( $, _, Backbone, Marionette, DataTableView) ->

  getParameterByName = (name, url) ->
    if not url then url = window.location.href
    name = name.replace(/[\[\]]/g, "\\$&")
    regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
    results = regex.exec(url)
    return null if not results
    return '' if not results[2]
    return decodeURIComponent(results[2].replace(/\+/g, " "))

  class DataRawView extends DataTableView
      el: '#raw-viz'

      onRender: =>
        @$('.DataTable').addClass('DataTable--fitContainer')
        super

      # Load up the intial set of data to render.
      initialize: (options) ->
        super options
        @collection.reset(document.initial_data)
        @listenTo Backbone, 'fetch:cluster', @fetch_cluster
        @listenTo Backbone, 'fetch:mine', @fetch_mine

      fetch_cluster: ->
        cluster = getParameterByName 'cluster_id'
        @collection.fetch data: cluster_id: cluster

      fetch_mine: -> @collection.reset(document.initial_data)


  return DataRawView
)
