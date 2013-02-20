/* ===================================================
 * dhlab_visualteam.js version 1.0 
 * ===================================================
 * Copyright 2013 dhlab_visualteam (Yoon Hong, HanYul Yoo, Seung Won)
 * ========================================================== */	

// main map object
var map;

$(function(){
	var mapdiv = '<div id="map" style="width: 100%; height: 100%; position: relative;" class="leaflet-container leaflet-fade-anim" tabindex="0"></div>'
	$(".display_leafletMap").append(mapdiv);
	createMap();	
	
	var circle = L.circle([32.73646, 242.86652], 10000, {
	    color: 'red',
	    fillColor: '#f03',
	    fillOpacity: 0.5
	});
	checkBoxEvent(circle);
	addLayerEvent();
	adddropdownEvent();
});

function createMap(){
	map = L.map('map').setView([32.73646, 242.86652], 10);
	L.tileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/997/256/{z}/{x}/{y}.png', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>'
		}).addTo(map);	
	var vTeamLayerControl = L.Control.extend({
		options: {
			position: 'topright'
		},		
		onAdd: function (map){
			var container = L.DomUtil.get("list");
			return container;}
	});	
	var vTeamAddButtonControl = L.Control.extend({
		options:{
			position: 'bottomleft'
		},
		onAdd: function (map){
			var container = L.DomUtil.get("addLayer");
			return container;
		}
	});	
	map.addControl(new vTeamAddButtonControl());	
	map.addControl(new vTeamLayerControl());
}

/*** checkBox Event handler ***/
// var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);
var currentLayer
function checkBoxEvent(polygon){
	currentLayer = polygon;
	$('#RedLayer').change(
		function(){
			if (this.checked){
				currentLayer.addTo(map);
			}
			else{
				map.removeLayer(currentLayer);
			}
   }
)};


function adddropdownEvent(){
  $('#dropdown').hover(			
	function () {
		//change the background of parent menu				
		$('#dropdown li a.parent').addClass('hover');
		//display the submenu
		$('#dropdown ul.children').show();
	},		
	function () {
		//change the background of parent menu
		$('#dropdown li a.parent').removeClass('hover');			
		//display the submenu
		$('#dropdown ul.children').hide();
	});
}

function addLayerEvent(){
	$('#addLayerdialog').hide();
	$('#addLayerButton').click(
		function() {
			$("#addLayerdialog").dialog({
				close: function(){
					$('#addLayer_form')[0].reset();}	
			});
	});	
	$(function(){
	  $("#confirm_add").click(function(){
		  var layerName = $('#layerName').val();
		  var layerId = $('#layerId').val();
		  $('#layerId').val().length
		  if( (layerName!='') && ( layerId != ''))
	      {
			  addLayer(layerName,layerId);
			  $(this).closest('.ui-dialog-content').dialog("close");
	      }
		  else{
			  var warning = 'You should fill both name and id';
			  alert(warning);
		  }		   	  
		});
	});	
	function addLayer(layerName, id){
		var newitem = '<li><input id=\"'+ id + '"type="checkbox">'+ " "+layerName + '</li>';
		$('.children').append(newitem);
	}
}