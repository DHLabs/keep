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

function jsGUIReady() {
	jsPlumb.ready( function() { 
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

		jsPlumb.addEndpoint($("#window0"), 
			sourceEndpoint );

		jsPlumb.addEndpoint($("#window2"), 
			targetEndpoint);

		jsPlumb.draggable($(".window"), { 
			grid: [20,20],
			containment: "parent" } );
		jsPlumb.bind("connectionDrag", function(connection) {
			console.log("connection " + connection.id + " is being dragged. suspendedElement is ", connection.suspendedElement, " of type ", connection.suspendedElementType);
		})
	});
};

function jsGUIAddWindow(question) {
	var tempID = "dynWindow_" + $(".window").length;
	/**
	$('<div class="window" id="' + id + '">').appendTo('body').html($(("#window0"))[0].innerHTML);
	console.log($("#" + id))

	jsPlumb.draggable($("#" + id), {
		grid: [20,20],
		containment: "parent"
	});
**/
	// Create the window first.
	var div = $('<div>', { id: tempID },
						 { class: 'window ui-draggable' } )
			  .css({
			  	left: '10em',
			  	top: '30em',
			  }).appendTo('#builder_gui');
  	jsPlumb.addEndpoint($(div), sourceEndpoint);
  	jsPlumb.addEndpoint($(div), targetEndpoint);
  	jsPlumb.draggable($(div), {
  		grid:[20,20],
  		containment: "parent"
  	});

  	// Start adding Text to the window
  	$('<div>', {
  		html: 'Name: ' + question.name,
  		id: tempID + '_name'
  	}).appendTo(div);
  	$('<div>', {
  		html: 'Title: ' + question.label,
  		id: tempID + '_label'
  	}).appendTo(div);
  	$('<div>', {
  		html: 'Type: ' + question.type,
  		id: tempID + '_type'
  	}).appendTo(div);

  	//$(div).append('<div id="' + tempID +'_name>Name: ' + question.name + '</div>');
  	//$(div).append('<div id="' + tempID +'_title>Label: ' + question.label + '</div>');
  	//$(div).append('<div id="' + tempID +'_type>Type: ' + question.type + '</div>');

  	$(div).addClass('window');
}

