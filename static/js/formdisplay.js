$(document).ready(function(){
    var i = -1;
    var size = 0;
    alert("this");

    $("#next").click(function(){
	$("#submit-xform").hide();
	size = $(".control-group").length; //used to determine last element
	$(".control-group").hide();
	i = i + 1;

	//TODO: do relevancy check on item i in while loop
	//if passes, display item i, exit loop
	//else, increment i, repeat loop

	$(".control-group").eq(i).show();
	$("#prev").show();
	
	//if element i is last element, hide next button, display submit button
	//else, display next button
	if ( i == size-1 ){
	    $("#next").hide();
	    $("#submit-xform").show();
	}else{
	    $("#next").show();
	}
    });

    $("#prev").click(function(){
	$("#next").show();
	$("#submit-xform").hide();
	$(".control-group").hide();
	i = i - 1;
	$(".control-group").eq(i).show();
	if (i == 0){
	    $("#prev").hide();
	}
    });

    $("#submit-xform").click(function(){
	alert("Thank you for your time!");
	//TODO: process form submit
    });
});
