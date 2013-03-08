//check if any handle is created
var isInitialized = false;
//range of the palette
var maxRange = 1020;
$(function() {
     $("#bttn2").click( function() {
		
        alert($("#slider-range").slider("values", 0));
    });
    
    $("#bttn3").click( function() {
        $("#slider-range").slider("disable");    
    });
    
    
    //mouse location
    $("#slider-range").click(function(e){
        //get clicked location
    	var x = e.pageX - this.offsetLeft;   
        $('#status2').html(x);
		if(!isInitialized || $( "#slider-range" ).slider( "option", "disabled" ))
			addHandle(x);
   });
});

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
    $("#slider-range").slider().find(".ui-slider-handle").append("<input class='slider_txt' type='text' style='margin-top: 43px; width: 27px; color:white; background:black; font-size:9px; border:none;'>");    
	if(textVals.length != 0) {
		$(".slider_txt").each(function() {
			$(this).val(textVals.pop());
		});
	}
};

//comparison function for number comparison
function compareNumbers(a,b) {
  return a - b;
}