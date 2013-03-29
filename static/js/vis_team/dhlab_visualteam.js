/* ===================================================
 * dhlab_visualteam.js version 1.0
 * ===================================================
 * Copyright 2013 dhlab_visualteam (Yoon Hong, HanYul Yoo, Seung Won)
 * ========================================================== */

//check if any handle is created
var isInitialized = false;
//range of the palette
var maxRange = 1023;

 // main map object
var map;
// layer array to keep layers
var layerArray=[];
var idCnt = 0;
	var testData={
	max: 46,
	data: [
	{lat: 33.5363, lon:-117.044, value: 50},
	{lat: 33.5608, lon:-117.24, value: 40},
	{lat: 38, lon:-97, value: 2},
	{lat: 38.9358, lon:-77.1621, value: 5},
	{lat: 38, lon:-97, value: 70},
	{lat: 54, lon:-2, value: 60},
	{lat: 51.5167, lon:-0.7, value: 20},
	{lat: 51.5167, lon:-0.7, value: 60},
	{lat: 60.3911, lon:5.3247, value: 10},
	{lat: 50.8333, lon:12.9167, value: 90},
	{lat: 50.8333, lon:12.9167, value: 60},
	{lat: 52.0833, lon:4.3, value: 70},
	{lat: 52.0833, lon:4.3, value: 80},
	{lat: 51.8, lon:4.4667, value: 10},
	{lat: 51.8, lon:4.4667, value: 11},
	{lat: 51.8, lon:4.4667, value: 19},
	{lat: 51.1, lon:6.95, value: 84},
	{lat: 13.75, lon:100.517, value: 46},
	{lat: 18.975, lon:72.8258, value: 77},
	{lat: 2.5, lon:112.5, value: 27},
	{lat: 25.0389, lon:102.718, value: 12},
	{lat: -27.6167, lon:152.733, value: 18},
	{lat: -33.7667, lon:150.833, value: 39},
	{lat: -33.8833, lon:151.217, value: 29},
	{lat: 9.4333, lon:99.9667, value: 50},
	{lat: 33.7, lon:73.1667, value: 40},
	{lat: 33.7, lon:73.1667, value: 30},
	{lat: 22.3333, lon:114.2, value: 54},
	{lat: 37.4382, lon:-84.051, value: 12}]
	};


$(function(){

	createMap();
	console.log( 'called' );

	$('#layerList').on("change", ":checkbox", function(event) {
		checkBoxEvent($(event.target).attr('id'));
	});

	$('#option_bttn').click(function() {
		if($(this).hasClass('bttn_nc')) {
			$(this).removeClass("bttn_nc").addClass("bttn_c");
			$('#gradient_select').removeClass("option_hidden").addClass("option_displayed");
		} else {
			$(this).removeClass("bttn_c").addClass("bttn_nc");
			$('#gradient_select').removeClass("option_displayed").addClass("option_hidden");
		}
	});


	//Taking care of adding a layer
	addLayerEvent();

	//Taking care of layer list
	adddropdownEvent();




     $("#bttn2").click( function() {
     	var rgbVal = $("#slider-range").slider("values", 0);
     	var rgb1;
     	var rgb2;
     	var rgb3;
     	//decide rgb color
     	if(rgbVal <= 255) {
			rgb1 = 0;
			rgb2 = rgbVal;
			rgb3 = 255;
		} else if(rgbVal <= 511) {
			rgb1 = 0;
			rgb2 = 255;
			rgb3 = 511 - rgbVal;
		} else if(rgbVal <= 767) {
			rgb1 = rgbVal - 512;
			rgb2 = 255;
			rgb3 = 0;
		} else {
			rgb1 = 255;
			rgb2 = 1023 - rgbVal;
			rgb3 = 0;
		}
		var result = 'rgb('+rgb1+','+rgb2+','+rgb3+')';
		$("#bttn2").css('color', result);
		//alert(getUserSetColors());


    });

    $("#colorAddBttn").click( function() {
		if(isInitialized)
			$("#slider-range").slider("disable");
		//make pin to follow mouse
		$("#pinImg").removeClass('hidden_pro');
		$("#slider-range").mousemove(function(e){
			$("#pinImg").css({left:e.pageX, top:e.pageY});

		});

    });

    //mouse location
    $("#slider-range").click(function(e){
        //get clicked location
//		alert(this.offsetLeft);
		//location of the leftend of the dialog window
		var windowLeft = parseInt($(".ui-dialog").css('left'));

    	var x = e.pageX - this.offsetLeft - windowLeft;
		if(!isInitialized || $( "#slider-range" ).slider( "option", "disabled" ))
			addHandle(x);
   });

});



function createMap(){
	map = L.map('map').setView([32.73646, 242.86652], 10);

	//base layer
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

	map.addControl(new vTeamLayerControl());
}

function checkBoxEvent(id) {
		var idx=parseInt(id.substring(5));
		$('#'+id).change(function() {
				if(this.checked) {
					layerArray[idx].addTo(map);
				} else {
					map.removeLayer(layerArray[idx]);
				}
		});
}

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
//	$('#addLayerdialog').hide();
	$('#addLayerButton').click(
		function() {
			$("#mapSelection").dialog({
				width: 450,
				position: "top",
				draggable: false,
				resizable: false,
				buttons: {
					"HeatMap": function() {
						$(this).dialog("close");
						$("#addLayerdialog").dialog({
							position: "top",
//							close: function(){
//								$('#addLayer_form')[0].reset();},
							width: 450,
							draggable: false,
							resizable: false
			//					position: {my:"top", at:"center", of:"window"}

						});
						var widget = $( "#addLayerdialog" ).dialog( "widget" );
						var buttons = widget.find(":button");
						buttons.addClass("addLayer_bttn");
						widget.find(".ui-dialog-titlebar-close").remove();
					//	widget.css('top', '-40em');
					},
					"OtherMap": function() {
					},
					"DifferentMap": function() {
					}
				}
				});
//					position: {my:"top", at:"center", of:"window"}
				var widget = $( "#mapSelection" ).dialog( "widget" );
				var buttons = widget.find(":button");
				buttons.addClass("mapSelect_bttn");

				var titleBar = widget.find(".ui-dialog-titlebar");
				titleBar.addClass("mapSelect_title");
				titleBar.removeClass("ui-dialog-titlebar");
				widget.find(".ui-dialog-titlebar-close").remove();
				//widget.css('top', '-40em');
	});

	$("#confirm_add").click(function(){
		var layerName = $('#layerName').val();
		var minVal = $('#minVal').val();
		var maxVal = $('#maxVal').val();

		if(layerName !== '' && minVal !== '' && maxVal !== '') {
			addLayer(layerName,'layer' + idCnt++, parseInt(minVal, 10), parseInt(maxVal, 10));
			$(this).closest('.ui-dialog-content').dialog("close");
		} else{
			var warning = 'You should fill both name, minVal and maxVal';
			alert(warning);
		}
	});
}

//Add layer to the list
function addLayer(layerName, id, minVal, maxVal){
	var newLayer = createHeatMap(minVal, maxVal);
	layerArray.push(newLayer);
	var newitem = '<li><input id=\"'+ id + '"type="checkbox">'+ " "+layerName + '</li>';
	$('.children').append(newitem);

}

function createHeatMap(minVal, maxVal) {
	var newDataArr = [];

	var options = {
	radius: 100000,// radius in pixels or in meters (see useAbsoluteRadius)
	useAbsoluteRadius: true, // true: r in meters, false: r in pixels
	color: 'transparent', // the color of the layer
	opacity: 0.5, // opacity of the not coverted area

	minValue: minVal,
	maxValue: maxVal
	};
	//build an array for the new layer
	for(var i = 0; i < testData.data.length; i++) {
		var temp = testData.data[i];
		if(minVal > temp.value || maxVal < temp.value)
			continue;

		newDataArr.push( [temp.lat, temp.lon, temp.value, ]);
	}

	var layer = L.TileLayer.maskCanvas(options, newDataArr);
	map.addLayer(layer);
}

// color slider
function addHandle(locVal) {
var widget = $('slider-range').slider("widget");
var temp1 = widget.find('#slider-range');
var temp2 = widget.find('.ui-slider-handle');
    var values = [];
	var textVals = [];
    if(isInitialized) {
        values = $("#slider-range").slider("values");
		//get values entered in the textboxes
		$(".slider_txt").each(function() {
			textVals.push($(this).val());
		});
        $("#slider-range").slider("destroy");
    } else {
        isInitialized = true;
    }

	//get width of the color range bar
	var barWidth = document.getElementById('slider-range').offsetWidth;
	//calculate the actual value to be inserted
	var ranVal = locVal*maxRange / barWidth;

	//take care of the corner case where new handle is
	//added before or within existing handels
	for(var i = 0; i < values.length; ++i)
		if(ranVal <= values[i]) {
			textVals.splice(i, 0, "");
			break;
		}

	//reorder arrays so they can reinserted properly
	textVals.reverse();
	values.push(ranVal);
    values.sort(compareNumbers);

	//create a new slider
	$("#slider-range").slider({
        min: 0,
        max: maxRange,
        values: values,
        slide: function( evt, ui ) {
            for(var i = 0, l = ui.values.length; i < l; i++){
                if(i !== l-1 && ui.values[i] > ui.values[i + 1]){
                    return false;
                } else if(i === 0 && ui.values[i] < ui.values[i - 1]){
                    return false;
                }
            }
        }
    });
    $("#slider-range").slider().find(".ui-slider-handle").append("<input class='slider_txt' type='text' style='margin-top: 43px; width: 35px; height:25px; color:white; background:transparent; font-size:8.5px; border:dotted; margin-left:-10px;'>");
	if(textVals.length != 0) {
		$(".slider_txt").each(function() {
			$(this).val(textVals.pop());
		});
	}

	//unbind pin img from mouse cursor
	$("#slider-range").unbind('mousemove');
	$("#pinImg").addClass('hidden_pro');
	$("#pinImg").offset({top: 0, left: 0});
};

//comparison function for number comparison
function compareNumbers(a,b) {
  return a - b;
}

//return user set colors
function getUserSetColors() {
	var textVals = [];
	var values = [];
	var ret = {};
	if(isInitialized) {
		values = $("#slider-range").slider("values");
		$(".slider_txt").each(function() {
			textVals.push($(this).val());
		});
	}

	//get rgb values
	var rgbVals = [];
	for(var i = 0; i < values.length; i++) {
		var rgbVal = values[i]
		var rgb1;
		var rgb2;
		var rgb3;
		//decide rgb color
		if(rgbVal <= 255) {
			rgb1 = 0;
			rgb2 = rgbVal;
			rgb3 = 255;
		} else if(rgbVal <= 511) {
			rgb1 = 0;
			rgb2 = 255;
			rgb3 = 511 - rgbVal;
		} else if(rgbVal <= 767) {
			rgb1 = rgbVal - 512;
			rgb2 = 255;
			rgb3 = 0;
		} else {
			rgb1 = 255;
			rgb2 = 1023 - rgbVal;
			rgb3 = 0;
		}
		var result = 'rgb('+rgb1+','+rgb2+','+rgb3+')';

		rgbVals.push(result);
	}

	for(var i=0; i<textVals.length; i++) {
		ret[textVals[i]] = values[i];
	}
	window.console.log("ret: " + ret.length);
	return ret;
}