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

var relevanceList = new Array();

/*
================
JSPlumb Specific code
Variables and Operations
Editing the source/target Endpoint variables
will change all source/target Endpoints on the 
page.
Note: Any element that takes an Endpoint MUST have the
'position:absolute' if it is to be moved around!  Without
the absolute position, the endpoints do not lock to the
element.
================
*/
var sourceEndpoint = {
	anchor: ["TopRight"],
	endpoint: ["Dot", {radius: 5}],
	paintStyle: {fillStyle: "#00F"},
	isSource: true,
	isTarget: false
}

var targetEndpoint = {
	anchor: ["Left"],
	endpoint: ["Dot", {radius: 5}],
	paintStyle: {fillStyle: "#F00"},
	isSource: false,
	isTarget: true,
	maxConnections:-1
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

	});
};


/*
================
GUI Windows (Screens) specific code
Window operations
================

	This function is used to create a new screen in the form
	GUI.  It is automatically called if no screens exist on
	creation of a question.
*/
function jsGUIAddWindow() {
	var windowID = "screen" + $(".window").length;
	var sortID = "sort" + $(".window").length;

	$('<div>', { id: windowID } )
	.css({
		left: '10em',
		top: '10em',
		position: 'absolute',
		backgroundColor: '#555555'
	}).addClass('window').appendTo('#builder_gui');

	//add hidden group settings
	$('<div>', { html: 'field-list'	})
	.css({
		visibility: 'hidden',
		padding: '0',
		'padding-bottom': '0',
		height: '0'
	}).addClass('hiddenGroupSettings').appendTo('#' + windowID);

	$('<ul>', { id: sortID }).appendTo('#' + windowID);

	//make the list sortable and add a placeholder!
	$('#' + sortID).sortable({
		connectWith: ".sortable",
		placeholder: "ui-state-highlight",
		stop: function(event, ui) {
			var tempList = $(ui.item).parent().parent().find('.relevanceList');
			if (tempList != undefined) {
				tempList.children('li').each(function() {
					jsPlumb.repaint(this);
				});
			}
		}
	}).addClass('sortable');

	//make the screen draggable!
	jsPlumb.draggable($('#' + windowID), { 
		grid: [20,20] });
	
	//add a div to hold the buttons
	$('<div>').addClass('windowButtons').appendTo('#' + windowID);

	//add a 'Add Relevances' button in the lower left corner
	$('<button>', {
		onclick: "jsGUIViewRelevance('" + windowID + "')",
		type: 'button',
		html: "<i class='icon-filter'></i> Add Relevance"
	}).addClass( 'relevance-icon' ).appendTo('#' + windowID + ' .windowButtons');

	//add a delete button in the lower right corner
	$('<button>', {
		onclick: "jsGUIDeleteWindow('" + windowID + "')",
		type: 'button',
		html: "<i class='icon-trash'></i> Delete"
	}).addClass( 'delete-icon' ).appendTo('#' + windowID + ' .windowButtons');

	//add a settings button right below "Add Relevances"
	$('<button>', {
		onclick: "jsGUIViewGroupSettings('" + windowID + "')",
		type: 'button',
		html: "<i class='icon-cog'></i> Group Settings"
	}).addClass( 'group-set-icon' ).appendTo('#' + windowID + ' .windowButtons');

	//add endpoints to the screen
	jsPlumb.addEndpoint($('#' + windowID), sourceEndpoint);
	jsPlumb.addEndpoint($('#' + windowID), targetEndpoint);
}

/* 
	Delete each element in a window, then delete
	the window.
*/
function jsGUIDeleteWindow(window) {
	$('#' + window + ' ul > li').each(
		function() {
			var questionID = $(this).attr('id');
			jsGUIDeleteQuestion(questionID);
		}
	);
	jsPlumb.remove($('#' + window));

	$('#' + window).remove();
}

function jsGUIViewGroupSettings(window) {
	$( '#groupSettingsWindow' ).dialog ({
		'width': 300
	});
	$( '#groupSettingsWindow' ).addClass(window);
}

/*
	Close the Group Modal, and add the group settings
	to the group list (at some point...)
*/
function jsGUICloseGroupSettingsDialog() {
	var windowSet = $("#groupSettingsWindow").attr('class');
	$("#groupSettingsWindow").removeClass(windowSet);
	var groupType = $("#groupTypeToggle").val().replace(' ', '-');

	console.log(groupType);
	if ($('#' + windowSet + ' .hiddenGroupSettings').html() != groupType) {
		$('#' + windowSet + ' .hiddenGroupSettings').html(groupType);
		console.log("Here");
	}


	$("#groupSettingsWindow").dialog ( 'close' );
}

/*
================
GUI Question specific code
Question operations
================

	This function adds a question to the form GUI.
	It is called in form_builder.js, before building
	the JSON.
*/
function jsGUIAddQuestion(question, currentQuestionName) {
	if (currentQuestionName == null) {
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

	  	// Start adding Text to the question
	  	$('<div>', {
	  		html: 'Question: ' + question.label,
	  		id: tempID + '_label'
	  	}).appendTo(div);
	  	$('<div>', {
	  		html: 'Type: ' + question.type,
	  		id: tempID + '_type'
	  	}).appendTo(div);

	  	// add the original name, but hide it!
	  	$('<div>', {
	  		html: question.name,
	  		id: tempID + '_name',
	  		style: 'display:none'
	  	} ).addClass('true-name').appendTo(div);

	  	//add an edit button in the lower left corner
		$('<button>', {
			onclick: "jsGUIEditQuestion('" + tempID + "')",
			type: 'button',
			html: "<i class='icon-edit'></i> Edit"
		}).addClass('edit-icon').appendTo(div);


		//add a delete button in the lower right corner
		$('<button>', {
			onclick: "jsGUIDeleteQuestion('" + tempID + "')",
			type: 'button',
			html: "<i class='icon-trash'></i> Delete"
		}).addClass( 'delete-icon' ).appendTo(div);

	  	$(div).addClass('question');
	  	$(div).addClass('ui-state-default');
	}

	else {
		jsGUIUpdateQuestion(question, currentQuestionName);
	}

	//jsGUIDFS();
}

/*
	This is called on an edit question operation, it is 
	used to update the question visuals.
*/
function jsGUIUpdateQuestion(question, currentQuestionName) {
	var updateQ = $('.true-name:contains(' + currentQuestionName + ')').closest('li').attr('id');
	$('#' + updateQ + '_label').text('Question: ' + question.label);
	$('#' + updateQ + '_type').text('Type: ' + question.type);
	$('#' + updateQ + '_name').text(question.name);
}

function jsGUIEditQuestion(question) {
	tempID = $('#' + question + '_name').html();
	editQuestion(tempID);
}

/*
	This function deletes the question from both the JSON
	and the GUI whenever the user clicks a question's 'delete'
*/
function jsGUIDeleteQuestion(question) {
	tempID = $('#' + question + '_name').html();
	deleteQuestion(tempID);
	$('#' + question).remove();
}


/*
================
GUI Relevances specific code
Relevance operations
================

	This function adds a relevance to the window.
	It also adds a node to the relevance, so it can be
	connected to other windows/screens.
*/

function jsGUIAddRelevance(window, relevance) {
	//first, see if there is a relevance list, if not, create one
	if ($('#' + window + ' .relevanceList').length < 1) {
		$('<h5 style="color:#FFF">Relevances:</h5>').appendTo('#' + window);
		$('<ul>')
		  .addClass('relevanceList')
		  .appendTo('#' + window);
	}
	
	var tempID = "relevance_" + $('.relevanceList').length + $('#' + window + ' .relevanceList li').length;
	//trying to keep the unique number, scramble (Randomize) it if it exists (sometimes occurs after deletion of relevances)
	while ($('#' + tempID).length > 0) {
		tempID = "relevance_" + Math.floor(Math.random() * 10000000);
	}

	//add a blank relevance to the relevance list!
	$('<li>', {
		id: tempID
	}).addClass('relevance')
	  .appendTo('#' + window + ' .relevanceList');

  	//add relevance text div to relevance item
  	$('<div>', {
  		id: tempID + "_text",
  		html: relevance.name + ': ' + relevance.conditions,
  	}).addClass('relevanceText').appendTo('#' + tempID);

	//add relevance edit and delete buttons
	$('<button>', {
		onclick: "jsGUIEditRelevance('" + tempID + "')",
		type: 'button',
		html: "<i class='icon-edit'></i>"
	}).addClass('edit-icon').appendTo('#' + tempID);

	$('<button>', {
		onclick: "jsGUIDeleteRelevance('" + tempID + "')",
		type: 'button',
		html: "<i class='icon-trash'></i>"
	}).addClass('delete-icon').appendTo('#' + tempID);

	// Add endpoint to the relevance
	jsPlumb.addEndpoint($('#' + tempID), sourceEndpoint);
}

function jsGUIEditRelevance(intakeRelevance) {

	
	if (intakeRelevance != null) {
		console.log("TODO: FIX RELEVANCE EDIT");
		return;
	}

	var relevance = new (function() {
		this.name = $("#relevanceQuestions").find(":selected").text();
		this.conditions = $("#relevanceBounds").val();
	});

	relevanceList.push(relevance);

	jsGUIAddRelevance($("#windowNameTracker")[0].innerHTML, relevance);

	jsGUICloseRelevance();
}

/*
	This function deletes the relevance from the GUI,
	and then repaints the Endpoints (Endpoints are annoying!)
*/
function jsGUIDeleteRelevance(relevance) {
	releParent = $('#' + relevance).parent();
	
	jsPlumb.remove($('#' + relevance));
	$('#' + relevance).remove();

	console.log(releParent);

	if (releParent.children('li').length < 1) {
		releParent.parent().find('h5').remove();
		releParent.remove();
	}

	else {
		releParent.children('li').each(function(){
			jsPlumb.repaint(this);
		});
	}
}

function jsGUIViewRelevance(window) {

	var flatQuestionList = buildFlatQuestionList();

	var selector = $('#relevanceQuestions')[0];
	$('#relevanceQuestions > option').remove();
	for (var i = 0; i < flatQuestionList.length; i++) {
		var relevanceOption = document.createElement('option');
		relevanceOption.innerHTML = flatQuestionList[i].label;
		relevanceOption.value = flatQuestionList[i].label + "_value";
		selector.appendChild(relevanceOption);
	}

	$('#windowNameTracker')[0].innerHTML = window;

	$( '#relevanceEditWindow' ).dialog({
		'width': 300
	});
}

function jsGUICloseRelevance() {
	$('#relevanceEditWindow').dialog( 'close' );
}
/*
================
Miscellaneous code
================
*/

function closeNameDialog() {
	$('#repositoryDefaultsWindow').dialog( 'close' );
}

/*
	This function runs a Depth-first search to build the question
	list and group list appropriately.  No JSON formatting here

	Returns array structured as the following:
		questionDictionary, 
		pathDictionary
*/

function jsGUIDFS() {
	var windowList = ['screen0'];

	// Dictionary in following form: "screen#": [questionIDs]
	var questionDictionary = {};

	// Dictionary in following form: "screen#: {attachScreen#: Relevance}
	// There can also be {settings: type} in the case of a group,
	// and {attachScreen#: none} in the case of a generic connection
	var pathDictionary = {};
	var i = "";

	$(".window").removeClass("visited-DFS")

	while (windowList.length > 0) {
		currentDiv = $('#' + windowList.pop());

		// Technically, should never happen, but if DFS is called w/o any elements
		if (currentDiv.length == 0) {
			break;
		}

		else if (currentDiv.hasClass("visited-DFS")) {
			continue;
		}
		else {
			currentDiv.addClass("visited-DFS");
			i = currentDiv.attr('id').substring(6);
		}

		var tempConnectionDict = {};
		
		// The case that there are no questions on the screen, another technicality
		if ($('#' + currentDiv.attr('id') + ' #sort' + i + ' li').length == 0) {
			console.log("This should NOT be hit.");
		}

		// Case of only one question on a screen
		else if ($('#' + currentDiv.attr('id') +  ' #sort' + i + ' li').length == 1) {
			var tempQ = $('#' + currentDiv.attr('id') +  ' #sort' + i + ' li .true-name').html();
			questionDictionary[i] = [tempQ];
		}

		//Case of multiple questions on a screen
		else {
			var tempQuestionArray = [];
			$('#' + currentDiv.attr('id') + ' #sort' + i + ' li').each( function() {
				tempQuestionArray.push($(this).find('.true-name').html());
			});
			questionDictionary[i] = tempQuestionArray;
			// Set the group settings 
			tempConnectionDict['settings'] = $(currentDiv).find('.hiddenGroupSettings').html();
		}

		// In the case of no connections, continue to the next screen
		if (jsPlumb.getConnections(currentDiv)[0] == undefined) {
			continue;
		}

		else {

			// This 'fun' bit of code is using jsPlumb to get the next screen	
			var tempConnectionID = jsPlumb.getEndpoints(currentDiv)[0].connections[0];
			if (tempConnectionID != undefined) {
				tempConnectionID = tempConnectionID.endpoints[1].elementId;
				windowList.push(tempConnectionID);
				tempConnectionDict[tempConnectionID.substring(6)] = "none";
			}

			// Code for handling the existence of relevances
			if ($(currentDiv).find('.relevanceList') != undefined) {
				$(currentDiv).find('.relevanceList li').each( function() {
					tempRelevanceText = $(this).find('.relevanceText').html();
					tempConnectionID = jsPlumb.getEndpoints($(this))[0].connections[0].endpoints[1].elementId;
					windowList.push(tempConnectionID);
					tempConnectionDict[tempConnectionID.substring(6)] = tempRelevanceText;
				});
			}

			pathDictionary[i] = tempConnectionDict;
		}
	}
	console.log(questionDictionary);
	console.log(pathDictionary);
	return [questionDictionary, pathDictionary];
}