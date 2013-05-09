var questionList = new Array();
var currentQuestion;

function questionTypeChanged() {
	var questionType = $("#questionType").val();

	removeChoices();
	removeConstraint();

	removeRelevance();//switch to showRelevance when relevances is ready

	if( questionType == "select one" || questionType == "select all that apply" ) {
		showChoices();
	} else if( questionType == "audio" ||questionType == "photo" || questionType == "video" || questionType == "barcode" ) {

	} else if( questionType == "geopoint" ) {

	} else if( questionType == "decimal" || questionType == "integer" ) {
		showConstraint();
	} else if( questionType == "text" ) {

	} else if( questionType == "note" ) {

	} else if( questionType == "date" ) {

	} else if( questionType == "dateTime" ) {

	} else if( questionType == "time" ) {

	}
}

function closeDialog() {
	$('#questionEditWindow').modal('hide');
}

function showRelevance() {
	var relevanceHTML = "<table class='table table-striped table-bordered'>"
	+ "<thead><tr><td colspan='3' style='background-color:#EEE;'>"
	+ "<h4><div class='pull-right'>"
	+ "<button type='button' onclick='addRelevance()'"
	+ " id='addrelevance' class='btn btn-small'>Add Relevance</button>"
	+ "</div>Relevances</h4></td></tr></thead><tbody id='relevanceList'></tbody></table>";

	$("#relevances").html(relevanceHTML);
}

function removeRelevance() {
	$("#relevances").html("");
}

function deleteConstraint(constraint) {
	var constraintId = "#" + constraint;
	$(constraintId).remove();
}

function addConstraint(constraintType, constraintValue) {

	var constraintNum = $("#constraintList tr").length;

	var html = "<tr id='constraint" + constraintNum + "'>\n";
	html += "<td><select id='constraintType" + constraintNum + "'>\n" +
	   "<option value='!='>Not Equal To</option>" +
	   "<option value='='>Equal To</option>" +
	   "<option value='&gt;'>Greater than</option>" +
	   "<option value='&lt;'>Less than</option>" +
	   "<option value='&gt;='>Greater than or equal to</option>" +
	   "<option value='&lt;='>Less than or equal to</option>" +
	   "</select>\n</td>\n";
	html += "<td><input id='constraintValue" + constraintNum
	   +"' placeholder='Constraint Value' value='" + constraintValue + "' type='number' step='any'></td>\n";
	html += "<td style='width:40px;text-align:center;'>"+
		"<button type='button' onclick='deleteConstraint(\"constraint" + constraintNum + "\")'"
		+ " class='btn btn-danger'>" +
		"   <i class='icon-trash'></i>"+
		"</button>"+
		"</td>\n</tr>\n";

	$("#constraintList").append( html );

	var constraintTypeId = "#constraintType" + constraintNum;
	if( constraintType != "" ) {
		$(constraintTypeId).val( constraintType );
	}

}

function showConstraint() {
	var constraintHTML = "<table class='table table-striped table-bordered'>\n"
	+ "<thead>\n<tr><td colspan='3' style='background-color:#EEE;'>\n"
	+ "<h4><div class='pull-right'>\n"
	+ "<select id='constraintType'>\n"
	+ "<option value='AND'>AND Constraints</option>\n"
	+ "<option value='OR'>OR Constraints</option>\n"
	+ "</select>\n"
	+ "<button type='button' onclick='addConstraint(\"\",\"\")'"
	+ " id='addconstraint' class='btn btn-small'>Add Constraint</button>\n"
	+ "</div>Contraints</h4></td></tr>\n</thead>\n<tbody id='constraintList'></tbody>\n</table>\n";

	$("#constraints").html(constraintHTML);
}

function removeConstraint() {
	$("#constraints").html("");
}

function showChoices() {
	var choiceHTML = "<table class='table table-striped table-bordered'>"
	+ "<thead><tr><td colspan='3' style='background-color:#EEE;'>"
	+ "<h4><div class='pull-right'>"
	+ "<button type='button' onclick='addChoice(\"\",\"\")'"
	+ " id='addchoice' class='btn btn-small'>Add Choice</button>"
	+ "</div>Choices</h4></td></tr></thead><tbody id='choiceList'></tbody></table>";

	$("#choices").html(choiceHTML);
}

function populateQuestion( questionNum ) {
	removeChoices();
	removeConstraint();
	removeRelevance();

	$("#questionName").val( "" );
	$("#questionLabel").val( "" );
	$("#questionRequired").checked = false;
	$("#questionHintUse").checked = false;
	$("#questionType").val('note');
	toggleHint();


	if( questionNum > -1 ) {
		var question = questionList[questionNum];
		$("#questionName").val( question.name );
		$("#questionLabel").val( question.label );
		$("#questionType").val(question.type);
		var choices = question.choices;
		if( choices ) {
			showChoices();
			for( var choice in choices ) {
				addChoice( choices[choice].name, choices[choice].label );
			}
		}

		var hint = question.hint;
		if( hint ) {
			$("#questionHintUse").checked = true;
			toggleHint();
			$("#questionHint").val(hint);
		}

		//TODO: relevance

		var bind = question.bind;
		if( bind ) {
			if( bind.required ) {
				$("#questionRequired").checked = true;
			}

			var constraintStr = bind.constraint;
			if( constraintStr ) {
				showConstraint();

				var theConstraints;
				if( constraintStr.indexOf( "AND" ) != -1 ) {
					$("#constraintType").val("AND");
					theConstraints = constraintStr.split("AND");
				} else {
					$("#constraintType").val("OR");
					theConstraints = constraintStr.split("OR");
				}

				for( var constraint in theConstraints ) {
					var constraintType;
					if( theConstraints[constraint].indexOf(">") != -1 ) {
						constraintType = ">";
					} else if( theConstraints[constraint].indexOf("<") != -1 ) {
						constraintType = "<";
					} else if( theConstraints[constraint].indexOf("<=") != -1 ) {
						constraintType = "<=";
					} else if( theConstraints[constraint].indexOf(">=") != -1 ) {
						constraintType = ">=";
					} else if( theConstraints[constraint].indexOf("=") != -1 ) {
						constraintType = "=";
					} else if( theConstraints[constraint].indexOf("!=") != -1 ) {
						constraintType = "!=";
					}
					var constraintValue = theConstraints[constraint].split( " " + constraintType + " " )[1];
					addConstraint(constraintType, constraintValue);
				}
			}
		}
	}
}

function toggleHint() {
	if( document.getElementById("questionHintUse").checked ) {
		var hintHTML = "<input id='questionHint' name='questionHint' type='text' placeholder='Hint'>";
		$("#questionHintDiv").html(hintHTML);
	} else {
		$("#questionHintDiv").html("");
	}
}

function removeChoices() {
	$("#choices").html("");
}

function addChoice(name, label) {

	var choiceNum = $("#choiceList tr").length;

	var html = "<tr id='choice" + choiceNum + "'>";
	html += "<td><input id='name' placeholder='Name' value='" + name +"' type='text'></td>";
	html += "<td><input id='label' placeholder='Label' value='"+label+"' type='text'></td>";
	html += "<td style='width:40px;text-align:center;'>"+
							"<button type='button' onclick='deleteChoice(\"choice" + choiceNum + "\")'"
								+" class='btn btn-danger'>"+
							 "   <i class='icon-trash'></i>"+
							"</button>"+
						"</td>";
	html += '</tr>';

	$("#choiceList").append( html );
}

function deleteChoice(choice) {
	var choiceId = "#" + choice;
	$(choiceId).remove();
}

function getIndivConstraintString(constraintNum) {

	var constraintType = $("#constraintType" + constraintNum).val();
	var constraintValue = $("#constraintValue" + constraintNum).val();

	var constraintString = ". " + constraintType + " " + constraintValue;

	return constraintString;
}

function okClicked() {

	if( validateQuestion() ) {
		var question;// = new Object();
		if( currentQuestion == -1 ) {
			question = new Object();
		} else {
			question = questionList[currentQuestion];
		}

		question.name = $("#questionName").val();
		question.label = $("#questionLabel").val();
		question.type = $("#questionType").val();

		if( $("#questionHintUse").checked ) {
			question.hint = $("#questionHint").val();
		}

		//TODO: bind(relevant),

		var useBind = false;
		var bind = new Object();

		if( document.getElementById("questionRequired").checked ) {
			bind.required = true;
			useBind = true;
		}

		//constraint
		var constraintList = document.getElementById("constraintList");
		if( constraintList ) {
			var numConstraints = constraintList.getElementsByTagName("tr").length;
			if( numConstraints > 0 ) {
				useBind = true;
				var constraintString = getIndivConstraintString( 0 );
				var constraintType = $("#constraintType").val();

				for( var index=1; index<numConstraints; index++ ) {
					constraintString += " " + constraintType + " " + getIndivConstraintString( index )
				}

				bind.constraint = constraintString;
			}
		}

		if( useBind ) {
			question.bind = bind;
		}

		if( question.type == 'select one' || question.type == 'select all that apply' ) {
			var choices = document.getElementById("choiceList").getElementsByTagName("TR");
			var options = new Array();
			for( var index=0; index<choices.length; index++ ) {
				var option = new Object();
				var child = choices.item(index);
				var rows = child.getElementsByTagName('INPUT');
				option.name = rows[0].value;
				option.label = rows[1].value;
				options.push(option);
			}
			question.choices = options;
		}

		//alert( JSON.stringify(question) );

		if( currentQuestion == -1 ) {
			questionList.push(question);
		} else {
			questionList[currentQuestion] = question;
		}
		buildSurvey();
		reloadQuestionListHTML();
		closeDialog();
	}
}

function buildSurvey() {
	var survey = new Object();
	survey.children = questionList;
	var value = JSON.stringify(survey);
	console.log( value );
	$("#id_survey_json").val(value);
}

function validateQuestion() {
	//TODO: finish this
	return true;
}

function deleteQuestion(questionNum) {
	var questionId = "#question" + questionNum;
	questionList.splice(questionNum, 1);
	$(questionId).remove();
}

function editQuestion(questionNum) {
	populateQuestion(questionNum);
	currentQuestion = questionNum;
	$('#questionEditWindow').modal('show');
}

function getHTMLForQuestion(questionNum) {

	var question = questionList[questionNum];
	var html = "<tr id='question" + questionNum + "'>";
	html += '<td>Name:&nbsp;' + question.name +
		'&nbsp;&nbsp;&nbsp;Label:' + question.label +
		'&nbsp;&nbsp;&nbsp;Question Type:' + question.type;
	html += '</td>';
	html += "<td style='width:70px;text-align:center;'>" +
							"<button class='btn btn-small' data-toggle='modal' onclick='editQuestion("+ questionNum + ")'>"+
							"	<i class='icon-pencil'></i> Edit"+
							"</button>"+
						"</td>"+
						"<td style='width:90px;text-align:center;'>"+
							"<button onclick='deleteQuestion(" + questionNum
								+")' class='btn btn-danger'>"+
							 "   <i class='icon-trash'></i> Delete"+
							"</button>"+
						"</td>";
	html += '</tr>';
	return html;
}

function reloadQuestionListHTML() {
	var html = '';

	for( var index=0; index<questionList.length; index++ ) {
		html = html + getHTMLForQuestion(index);
	}

	$("#questionList").html( html );
}