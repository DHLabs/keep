/*
================
FORM BUILDER GUI
This javascript file is strictly for building
the GUI used on the create new form page.  There
is significant use of JSPlumb and JQuery UI, so if
you are having problems understanding what is being
done, check those documentations for additional
reference.
================
*/

var sourceEndpoint = {
	anchor: ["Right"],
	endpoint: ["Dot", {radius: 5}],
	paintStyle: {fillStyle: "#000"},
	isSource: true,
	isTarget: false
}

var targetEndpoint = {
	anchor: ["Left"],
	endpoint: ["Dot", {radius: 5}],
	paintStyle: {fillStyle: "#F00"},
	isSource: false,
	isTarget: true
}

/*
	This function is used to create and prepare the jsGUI
	for form creation.  It is called when the user clicks
	"Create New Survey" on the new form page.
*/
function jsGUIReady() {
	jsPlumb.ready( function() { 

		// JSPlumb Modified Defaults for us.  Flowchart has better
		// Connectors than the default Bezier.
		jsPlumb.importDefaults({					
			Connector: [ "Flowchart", { stub:10 } ],
			Container: $('#builder_gui'),
			DragOptions: { cursor: 'pointer', zIndex: 2000 },
			PaintStyle: {
				strokeStyle: '#000',
				lineWidth:3
			},
			Overlays:[
				["Arrow", { width:15, 
							length:15,
							direction:1,
							foldback:0.5, 
							location:0.75, 
							id:'arrow' 
				}]
			]
		})

		// Debugging message, tells what is being connected.
		jsPlumb.bind("connectionDrag", function(connection) {
			console.log("connection " + connection.id + " is being dragged. suspendedElement is ", connection.suspendedElement, " of type ", connection.suspendedElementType);
		})
	});
};

/*
	This function is used to create a new screen in the form
	GUI.  It is automatically called if no screens exist on
	creation of a question.
*/
function jsGUIAddWindow() {
	var windowID = "screen" + $(".window").length;
	var sortID = "sort" + $(".window").length;

	$('<div>', { id: windowID },
			   { class: 'window ui-draggable' } )
	.css({
		left: '10em',
		top: '2em',
	}).appendTo('#builder_gui');

	$('<ul>', { id: sortID },
			  { class: 'sortable' }
	 ).appendTo('#' + windowID);

	//make the list sortable and add a placeholder!
	$('#' + sortID).sortable({
		placeholder: "ui-state-highlight"
	});

	//make the screen draggable!
	$('#' + windowID).draggable({ 
		grid: [20,20],
		containment: "parent" });

	//make the screen a window again...
	$('#' + windowID).addClass('window');

	//add the sortable css class back in to the list...
	$('#' + sortID).addClass('sortable');

	//center the list in the screen
	$('#' + sortID).center({
		vertical: false
	});

	//add endpoints to the screen
	jsPlumb.addEndpoint($('#' + windowID), sourceEndpoint);
	jsPlumb.addEndpoint($('#' + windowID), targetEndpoint);
}

/*
	This function adds a question to the form GUI.
	It is called in form_builder.js, before building
	the JSON.
*/
function jsGUIAddQuestion(question) {
	var tempID = "dynQuestion_" + $(".question").length;
	
	// Create the window first, if none exists
	if ($(".window").length < 1) {
		jsGUIAddWindow();
	}

	var recentSort = "sort" + ($(".sortable").length - 1);

	//Create the question
	var div = $('<li>', { id: tempID },
						 { class: 'question' } )
			  .appendTo('#' + recentSort);

  	// Start adding Text to the window
  	console.log($(".sortable").length - 1);
  	$('<div>', {
  		html: 'Question: ' + question.label,
  		id: tempID + '_label'
  	}).appendTo(div);
  	$('<div>', {
  		html: 'Type: ' + question.type,
  		id: tempID + '_type'
  	}).appendTo(div);

  	$(div).addClass('question');
  	$(div).addClass('ui-state-default');
}

