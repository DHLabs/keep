var questionList = new Array();
var currentQuestion;
var currentQuestionName;
var currentGroupName;

function questionTypeChanged() {
	var questionType = $("#questionType").val();

  	removeChoices();
  	removeConstraint();

	removeRelevance();//switch to showRelevance when relevances is ready

  	if( questionType == "select one" || questionType == "select all that apply" ) {
  		showChoices();
  		showConstraint();
  	} else if( questionType == "audio" ||questionType == "photo" || questionType == "video" || questionType == "barcode" ) {

	} else if( questionType == "geopoint" ) {

	} else if( questionType == "decimal" || questionType == "integer" ) {
		showConstraint();
	} else if( questionType == "text" ) {

	} else if( questionType == "note" ) {

  	} else if( questionType == "date" || questionType == "dateTime" || questionType == "time") {
  		showConstraint();
  	}
}

function closeDialog() {
	$('#questionEditWindow').modal('hide');
}

function getValueInputForType(questionType, tagId) {
	
	var html = "<input id='" + tagId + "";
	var inputType = "text";
	if( questionType == "decimal" || questionType == "integer" ) {
		inputType = 'number';
	} else if ( questionType == "date" ) {
		inputType = 'date';
	} else if(questionType == "dateTime") {
		inputType = 'datetime-local';
	} else if(questionType == "time") {
		inputType = 'time';
	} else if( questionType == "select one" || questionType == "select all that apply" ) {
		inputType = 'number';
	}
	html += "";
}

function getCompareSelectForType(questionType, tagId) {

	var html = "<select id='" + tagId + "'>\n";
	
	if( questionType == "decimal" || questionType == "integer" ) {
		html += "<option value='!='>Not Equal To</option>" +
	     "<option value='='>Equal To</option>" +
	     "<option value='&gt;'>Greater than</option>" +
	     "<option value='&lt;'>Less than</option>" +
	     "<option value='&gt;='>Greater than or equal to</option>" +
	     "<option value='&lt;='>Less than or equal to</option>";
	} else if ( questionType == "date" || questionType == "dateTime" || questionType == "time" ) {
		html += "<option value='!='>Not Equal To</option>" +
	    "<option value='='>Equal To</option>" +
	    "<option value='&gt;'>Later than</option>" +
	    "<option value='&lt;'>Earlier than</option>" +
	    "<option value='&gt;='>Later than or equal to</option>" +
	    "<option value='&lt;='>Earlier than or equal to</option>";
	} else if( questionType == "select one" || questionType == "select all that apply" ) {
		html += "<option value='='>Selected</option>" +
	   "<option value='!='>Not Selected</option>";
	}
	    
	html += "</select>\n";
	return html;
}

function addRelevance(questionName,relevantType,relevantValue) {
	var relevantNum = $("#relevanceList tr").length;

	var html = "<tr id='relevance" + relevantNum + "'>\n<td>\n";
	html += "<select id='relevantQuestion" + relevantNum + " onchange='>\n";

    //TODO: fix this with flat questionList
	for( var questionIndex=0; questionIndex<currentQuestion; questionIndex++ ) {
		html+= "<option value='" + questionIndex + "'>" + 
		questionList[questionIndex].name + "</option>\n"
	}
    
	html += "</select>\n</td>\n";
	html += "<td id='relevantType"+ relevantNum +"''></td>\n";//relevantType selection
	html += "<td id='relevantValue"+ relevantNum +"'></td>\n";//relevantValue

	html += "<td style='width:40px;text-align:center;'>"+
        "<button type='button' onclick='deleteConstraint(\"constraint" + constraintNum + "\")'" 
        + " class='btn btn-danger'>" +
        "   <i class='icon-trash'></i>"+
        "</button>"+
		"</td>\n</tr>\n";

	if( questionName ) {
		$("#relevantQuestion" + relevantNum).val( questionName );

		if( relevantType ) {
			relevanceQuestionChanged( relevantNum, questionName );
			if(  relevantValue ) {
				$("#relevanceValue"+relevanceNum).val( relevantValue );
			}
		}
	}
}

function relevanceQuestionChanged( relevanceNum, questionName ) {

	var typeTag = 'relevanceType' + relevanceNum;
	var valueTag = 'relevanceValue' + relevanceNum;
	var html = getCompareSelectForType( questionList[questionNum].type, typeTag );
	$("#relevantType"+relevanceNum).html( html );

    var question = getQuestionForName(questionName);

	$("#relevantValue"+relevanceNum).html( getValueInputForType( 
		getValueInputForType( question.type ), valueTag ) );
}

function showRelevance() {
	var relevanceHTML = "<table class='table table-striped table-bordered'>"
	+ "<thead><tr><td colspan='4' style='background-color:#EEE;'>"
	+ "<h4><div class='pull-right'>"
	+ "<select id='relevanceType'>\n"
	+ "<option value='AND'>AND Relevances</option>\n"
	+ "<option value='OR'>OR Relevances</option>\n"
	+ "</select>\n"
	+ "<button type='button' onclick='addRelevance(-1,null,null)'"
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

	var html = "<tr id='constraint" + constraintNum + "'>\n<td>\n";

	var questionType = $("#questionType").val();

	var selectId = "constraintType" + constraintNum;
	html += getCompareSelectForType( questionType, selectId );
	html += "</td>\n";

	if( questionType == "decimal" || questionType == "integer" ) {
		

	   html += "<td><input id='constraintValue" + constraintNum 
	     +"' placeholder='Constraint Value' value='" + constraintValue + 
	     "' type='number' step='any'></td>\n";
	} else if( questionType == "date" ) {
		

	   html += "<td><input id='constraintValue" + constraintNum 
	   +"' placeholder='Constraint Value' value='" + constraintValue + 
	   "' type='date'></td>\n";
	} else if( questionType == "dateTime" ) {
		

	   html += "<td><input id='constraintValue" + constraintNum 
	   +"' placeholder='Constraint Value' value='" + constraintValue + 
	   "' type='datetime-local'></td>\n";
	} else if( questionType == "time" ) {
		

	   html += "<td><input id='constraintValue" + constraintNum 
	   +"' placeholder='Constraint Value' value='" + constraintValue + 
	   "' type='time'></td>\n";
	} else if( questionType == "select one" || questionType == "select all that apply" ) {
		

	   html += "<td><input id='constraintValue" + constraintNum 
	   +"' placeholder='Constraint Value' value='" + constraintValue + 
	   "' type='text'></td>\n";
	}
	
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

function populateQuestion( questionName ) {
	removeChoices();
	removeConstraint();
	removeRelevance();

    $("#questionName").val( "" );
	$("#questionLabel").val( "" );
	$("#questionRequired").checked = false;
	$("#questionHintUse").checked = false;
	$("#questionType").val('note');
	toggleHint();

	if( questionName != null ) {
        var question = getQuestionForName(questionName);
        
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

			var relevantStr = bind.relevant;
			//TODO: finish relevance
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
	html += "<td><input id='name' placeholder='Name' onKeyUp='sanitizeNameInput(this)'' value='" + name +"' type='text'></td>";
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

	var constraintType =  $("#constraintType" + constraintNum).val();
	var constraintValue = $("#constraintValue" + constraintNum).val();

	var constraintString = ". " + constraintType + " " + constraintValue;

	return constraintString;
}

function getIndivRelevanceString( relevanceNum ) {
	var relevanceQuestionName = $("#relevanceQuestion" + relevanceNum).val();
	var relevanceQuestion = getQuestionForName(relevanceQuestionName);

	var relevanceType =  $("#relevanceType" + relevanceNum).val();
	var relevanceValue = $("#relevanceValue" + relevanceNum).val();

	var relevanceString = "${" + relevanceQuestion.name + "}";
	relevanceString += " " + relevanceType + " " + relevanceValue;

	return relevanceString;
}

function okClicked() {

	if( validateQuestion() ) {
		var question;// = new Object();
		if( currentQuestionName == null ) {
			question = new Object();
		} else {
			question = getQuestionForName( currentQuestionName );
		}

		question.name = $("#questionName").val();
		question.label = $("#questionLabel").val();
		question.type = $("#questionType").val();

		if( $("#questionHintUse").checked ) {
			question.hint = $("#questionHint").val();
		}

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

		//relevances
		var relevanceList = document.getElementById("relevanceList");
		if( relevanceList ) {
			var numRelevants = relevanceList.getElementsByTagName("tr").length;
			if( numRelevants > 0 ) {
				useBind = true;
				var relevanceString = getIndivRelevanceString( 0 );
				var relevanceType = $("#relevanceType").val();

				for( var index=1; index<numRelevants; index++ ) {
					relevanceString += " " + relevanceType + " " + getIndivRelevanceString( index );
				}

				bind.relevant = relevanceString;
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

        if( question.type == "group" && currentQuestionName == null ) {
            question.children = new Array();
        }

        if( currentGroupName ) {

            var group = getQuestionForName(currentGroupName);

            if( currentQuestionName == null ) {
                group.children.push(question);
            } else {
                var questionIndex = -1;
                for( var index in group.children ) {
                    if( group.children[index].name == question.name ) {
                        questionIndex = index;
                        break;
                    }
                }
                if( questionIndex == -1 ) {
                    console.log( "could not find question to modify" );
                } else {
                    group.children[questionIndex] = question;
                }
                
            }
        } else {

            if( currentQuestionName == null ) {
                questionList.push(question);
            } else {
                var questionIndex = -1;
                for( var index in questionList ) {
                    if( questionList[index].name == question.name ) {
                        questionIndex = index;
                        break;
                    }
                }
                if( questionIndex == -1 ) {
                    console.log( "could not find question to modify" );
                } else {
                    questionList[questionIndex] = question;
                }
            }
        }
		
		buildSurvey();
		reloadQuestionListHTML();
		closeDialog();
        currentGroupName = null;
	}
}

function buildFlatQuestionList() {
    var flatList = new Array();
    buildQuestionList( flatList, questionList );
    return flatList;
}

function buildQuestionList( listQuestions, formChildren )  {

	for( var i=0; i<formChildren.length; i++ ) {
		var question = formChildren[i];
		if( question.type == "group" ) {
			buildQuestionList( listQuestions, question.children );
		} else if( question.type == 'note' ) {
			//don't add note
		} else if( question.type == 'note' ) {

		} else {
			questionList.push( question );
		}
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

	//name (needs to be there)
	if( $( '#questionName' ).val() == '' ) {
		//TODO: display that name is needed
		return false;
	}

    //TODO: check to make sure question name is not repeated

	//constraints (make sure all have names and values)

	//choices (all choices need names and values)
	if( $('#questionType').val() == 'select one' || $('#questionType').val() == 'select all that apply' ) {

		var choicetd = document.getElementById( 'choiceList' ).getElementsByTagName( 'tr' );
		for( var i=0; i<choicetd.length; i++ ) {

			var inputs = choicetd.item(i).getElementsByTagName('input');
			for( var i2=0; i2<inputs.length; i2++ ) {
				if( !inputs.item(i2).value || inputs.item(i2).value == '' ) {
					//TODO: alert
					return false;
				}
			}
		}
	}

	//relevance
	//TODO:

	return true;
}

function deleteQuestion(questionName) {
    //TODO: fix this

	var questionId = "#question" + questionName;

    var question = getQuestionForName(questionName);
    
    if( currentGroupName ) {

        var group = getQuestionForName(currentGroupName);

        var questionIndex = -1;
        for( var index in group.children ) {
            if( group.children[index].name == question.name ) {
                questionIndex = index;
                break;
            }
        }
        if( questionIndex == -1 ) {
            console.log( "could not find question to delete" );
        } else {
            group.children.splice(questionIndex,1);
        }

    } else {
        var questionIndex = -1;
        for( var index in questionList ) {
            if( questionList[index].name == question.name ) {
                questionIndex = index;
                break;
            }
        }
        if( questionIndex == -1 ) {
            console.log( "could not find question to delete" );
        } else {
            questionList.splice(questionIndex, 1);
        }
    }

	//questionList.splice(questionNum, 1);

    //remove the question from the interface
	$(questionId).remove();
}

function editQuestion(questionName) {
    populateQuestion(questionName);
	currentQuestionName = questionName;
	$('#questionEditWindow').modal('show');
}

function sanitizeNameInput(inputElement) {
	var inputString = inputElement.value;
	inputString = inputString.split(' ').join('_')
	inputElement.value = inputString;
}

function getHTMLForQuestion(question) {

    if( question.type == "group" ) {
        var groupHTML = "<tr id='question" + question.name + "'>" +
        "<td colspan='3'><table class='table table-striped table-bordered'>\n"
        + "<thead>\n<tr><td colspan='3' style='background-color:#EEE;'>\n"
        + "<h4>"+ question.name +"<div class='pull-right'>\n"
        + "<button type='button' onclick=\"addQuestionToGroup('"
        + question.name +"')\""
        + " id='addQuestionForGroup' class='btn btn-small'>Add Question</button>\n" +
        "<button class='btn btn-small' data-toggle='modal' onclick=\"editQuestion('"+ question.name + "')\">"+
        "	<i class='icon-pencil'></i> Edit"+
        "</button>"+
        "<button onclick=\"deleteQuestion('" + question.name
        +"')\" class='btn btn-danger'>"+
        "   <i class='icon-trash'></i> Delete"+
        "</button></div></h4></td></tr>\n</thead>\n<tbody>";

        //generate html from other questions
        for( var groupQuestion in question.children ) {
            groupHTML += getHTMLForQuestion( question.children[groupQuestion] );
        }        
        
        groupHTML += "</tbody>\n</table></td></tr>\n";

        return groupHTML;
    } else {
        var html = "<tr id='question" + question.name + "'>";
        html += '<td>Name:&nbsp;' + question.name +
		'&nbsp;&nbsp;&nbsp;Label:' + question.label +
		'&nbsp;&nbsp;&nbsp;Question Type:' + question.type;
        html += '</td>';
        html += "<td style='width:70px;text-align:center;'>" +
        "<button class='btn btn-small' data-toggle='modal' onclick=\"editQuestion('"+ question.name + "')\">"+
        "	<i class='icon-pencil'></i> Edit"+
        "</button>"+
        "</td>"+
        "<td style='width:90px;text-align:center;'>"+
        "<button onclick=\"deleteQuestion('" + question.name
        +"')\" class='btn btn-danger'>"+
        "   <i class='icon-trash'></i> Delete"+
        "</button>"+
        "</td>";
        html += '</tr>';
        return html;
    }
}

function addQuestionToGroup( groupName ) {
    currentGroupName = groupName;
    editQuestion( null );
}

function getQuestionForName(questionName, listQuestions ) {

    if( !listQuestions ) {
        listQuestions = questionList;
        currentGroupName = null;
    }

    for( var question in listQuestions ) {

        if( listQuestions[question].name == questionName ) {
            return listQuestions[question];
        } else {
            if( listQuestions[question].type == "group" ) {
                var theQuestion = getQuestionForName( questionName, listQuestions[question].children );
                if( theQuestion ) {
                    currentGroupName = listQuestions[question].name;
                    return theQuestion;
                }
            }
        }
    }
    currentGroupName = null;
    return null;
}

function reloadQuestionListHTML() {
	var html = '';
	for( var question in questionList ) {
		html = html + getHTMLForQuestion(questionList[question]);
	}

	$("#questionList").html( html );
}
