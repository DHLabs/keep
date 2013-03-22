//check if any handle is created
var isInitialized = false;
//range of the palette
var maxRange = 1023;
$(function() {
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
		alert(result);
     	
    });
    
    $("#bttn3").click( function() {
		if(isInitialized)
			$("#slider-range").slider("disable");   
		//make pin to follow mouse
		$("#pinImg").removeClass('hidden_pro');
		$("#slider-range").mousemove(function(e){
			$("#pinImg").css({left:e.pageX+1, top:e.pageY});
			
		});

    });
    
    //mouse location
    $("#slider-range").click(function(e){
        //get clicked location
    	var x = e.pageX - this.offsetLeft;   
		if(!isInitialized || $( "#slider-range" ).slider( "option", "disabled" ))
			addHandle(x);
   });
   
/*   	$('#slider-range').on("mousedown", ".ui-slider-handle", function(event) {
		//get proportional values
		var p = $(event.target).prev().css('left');
		if(p!=null)
			p = p.substring(0,3);
		var pVal = $(event.target).prev().children('.slider_txt').val();
		var n = $(event.target).next().css('left').substring(0,3);
		if(n!=null)
			n = n.substring(0,3);
		var nVal = $(event.target).next().children('.slider_txt').val();
		var c = $(event.target).css('left').substring(0,3);
		var x = (c-p)*(nVal-pVal)/(n-p);
		
		$(event.target).children('.slider_txt').val(p+x);
	});

	
	$('#slider-range').on("change", "#.slider_txt", function(event) {
		$(".slider_txt").each(function() {
			if($(this).val().length < 1) {
				blink($(this));
			}
		});
	});
	*/
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
    $("#slider-range").slider().find(".ui-slider-handle").append("<input class='slider_txt' type='text' style='margin-top: 43px; width: 25px; color:white; background:black; font-size:9px; border:none; margin-left:-7px;'>");    
	if(textVals.length != 0) {
		$(".slider_txt").each(function() {
			$(this).val(textVals.pop());
		});
	}
	
	//unbind pin img from mouse cursor
	$("#slider-range").unbind('mousemove');
	$("#pinImg").addClass('hidden_pro');
	$("#pinImg").offset({top: 0, left: 1000});
	
	$(".slider_txt").each(function() {
		var textVal = $(this).val();
		if(textVal.length<1) {
			blinkBlink($(this));
		}
	});	
};

//comparison function for number comparison
function compareNumbers(a,b) {
  return a - b;
}

//make the textbox to blink
function blink(selector){
	$(selector).fadeOut('slow', function(){
	$(this).fadeIn('slow', function(){
	blink(this);
	});
	});
}
