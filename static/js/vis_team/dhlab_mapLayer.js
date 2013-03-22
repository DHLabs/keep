var MAXLENGTH = 1024;
var MAXAREA = 256;
var gMinValue;
var gMaxValue;

L.TileLayer.MaskCanvas = L.TileLayer.Canvas.extend({
	options: {
        radius: 5,
        useAbsoluteRadius: true,  // true: r in meters, false: r in pixels
        color: '#000',
        opacity: 0.5,
        debug: false,
		
		// custom options
		minValue: 0,
		maxValue: 100
	},

	initialize: function (options, dataArr) {
        var self = this;
        L.Util.setOptions(this, options);
		
		gMinValue = self.options.minValue;
		gMaxValue = self.options.maxValue;
		
        this.drawTile = function (tile, tilePoint, zoom) {
            var ctx = {
                canvas: tile,
                tilePoint: tilePoint,
                zoom: zoom
            };
			self._drawDebugInfo(ctx);
            this._draw(ctx);
        };
		if(dataArr != null)
			this.setData(dataArr);	
    },

    _drawDebugInfo: function (ctx) {
        var max = this.tileSize;
        var g = ctx.canvas.getContext('2d');
        g.globalCompositeOperation = 'destination-over';
        g.strokeStyle = '#000000';
        g.fillStyle = '#FFFFFF';
        g.strokeRect(0, 0, max, max);
        g.font = "12px Arial";
        g.fillRect(0, 0, 5, 5);
        g.fillRect(0, max - 5, 5, 5);
        g.fillRect(max - 5, 0, 5, 5);
        g.fillRect(max - 5, max - 5, 5, 5);
        g.fillRect(max / 2 - 5, max / 2 - 5, 10, 10);
        g.strokeText(ctx.tilePoint.x + ' ' + ctx.tilePoint.y + ' ' + ctx.zoom, max / 2 - 30, max / 2 - 10);
    },

    _createTile: function () {
        var tile = this._canvasProto.cloneNode(false);
        tile.onselectstart = tile.onmousemove = L.Util.falseFn;

        var tileSize = this.options.tileSize;
        var g = tile.getContext('2d');
        g.fillStyle = this.options.color;
        g.fillRect(0, 0, tileSize, tileSize);
        g.globalCompositeOperation = 'destination-out';
        return tile;
    },

    setData: function(dataset) {
/*		if(dataset != null || dataset.length > 0)
			window.console.log(dataset.length);
*/	
        var self = this;

        this.bounds = new L.LatLngBounds(dataset);

        this._quad = new QuadTree(this._boundsToQuery(this.bounds), false, 6, 6);

        dataset.forEach(function(d) {
            self._quad.insert({
                x: d[1], //lng
                y: d[0], //lat
				z: d[2]
            });
		//	window.console.log("d[2]: " + d[2]);
        });
        this.redraw();
    },

    _tilePoint: function (ctx, coords) {
        // start coords to tile 'space'
        var s = ctx.tilePoint.multiplyBy(this.options.tileSize);

        // actual coords to tile 'space'
        var p = this._map.project(new L.LatLng(coords[0], coords[1]));

        // point to draw
        var x = Math.round(p.x - s.x);
        var y = Math.round(p.y - s.y);
        return [x, y];
    },

    _drawPoints: function (ctx, coordinates) {
       	var c = ctx.canvas,
            g = c.getContext('2d'),
            self = this,
            p;
			coordinates.forEach(function(coords){
            p = self._tilePoint(ctx, coords);
			g.fillStyle = rgbHelper(coords[2]);
			window.console.log (rgbHelper(coords[2]));
            g.beginPath();
            g.arc(p[0], p[1], self._getRadius(), 0, Math.PI * 2);
            g.fill();
        });
    },

    _boundsToQuery: function(bounds) {
        return {
            x: bounds.getSouthWest().lng,
            y: bounds.getSouthWest().lat,
            width: bounds.getNorthEast().lng-bounds.getSouthWest().lng,
            height: bounds.getNorthEast().lat-bounds.getSouthWest().lat
        };
    },

    _getLatRadius: function () {
        return (this.options.radius / 40075017) * 360;
    },

    _getLngRadius: function () {
        return this._getLatRadius() / Math.cos(L.LatLng.DEG_TO_RAD * this._latlng.lat);
    },

    // call to update the radius
    projectLatlngs: function () {
        var lngRadius = this._getLngRadius(),
            latlng2 = new L.LatLng(this._latlng.lat, this._latlng.lng - lngRadius, true),
            point2 = this._map.latLngToLayerPoint(latlng2),
            point = this._map.latLngToLayerPoint(this._latlng);
        this._radius = Math.max(Math.round(point.x - point2.x), 1);
    },

    // the radius of a circle can be either absolute in pixels or in meters
    _getRadius: function() {
        if (this.options.useAbsoluteRadius) {
            return this._radius;
        } else{
            return this.options.radius;
        }
    },

    _draw: function (ctx) {
        if (!this._quad || !this._map) {
            return;
        }

        var tileSize = this.options.tileSize;

        var nwPoint = ctx.tilePoint.multiplyBy(tileSize);
        var sePoint = nwPoint.add(new L.Point(tileSize, tileSize));

        if (this.options.useAbsoluteRadius) {
            var centerPoint = nwPoint.add(new L.Point(tileSize/2, tileSize/2));
            this._latlng = this._map.unproject(centerPoint);
            this.projectLatlngs();
        }

        // padding
        var pad = new L.Point(this._getRadius(), this._getRadius());
        nwPoint = nwPoint.subtract(pad);
        sePoint = sePoint.add(pad);

        var bounds = new L.LatLngBounds(this._map.unproject(sePoint), this._map.unproject(nwPoint));

        var coordinates = [];
        this._quad.retrieveInBounds(this._boundsToQuery(bounds)).forEach(function(obj) {
            coordinates.push([obj.y, obj.x, obj.z]);
		//	window.console.log("obj.z: " + obj.z);
        });

        this._drawPoints(ctx, coordinates);

        var c = ctx.canvas;
        var g = c.getContext('2d');
    }
});

function rgbHelper(val){
	var pColor = parseInt(val / ( gMaxValue - gMinValue) * MAXLENGTH);	
	var range = parseInt(pColor / MAXAREA);
	var remainder = parseInt(pColor % MAXAREA);
	
	//window.console.log ("val: " + val);
	//window.console.log ("pColor: " + pColor);
	window.console.log ("range: " + range);
	window.console.log ("remainder: " + remainder);
	var rString = 'rgb(';
	switch (range)
	{
		case 0:
			return rString + '0,' + remainder.toString() + ',256)';
		case 1: 
			return rString + '0,' + '256,' + (MAXAREA - remainder).toString();
		case 2: 
			return rString + remainder.toString() + ',256,0)';
		case 3:
			return rString + '255,' + (MAXAREA - remainder).toString() + ',0)';
		default:
			window.console.log("Error in switch!");
	}		
}


L.TileLayer.maskCanvas = function (options, dataArr) {	
    return new L.TileLayer.MaskCanvas(options, dataArr);
};