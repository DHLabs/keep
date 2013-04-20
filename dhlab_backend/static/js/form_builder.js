var questionList = new Array();

$(document).ready(function(){

  $("#addquestion").click(function(){
  	                                              
  });

  $("#questionType").click(function(){

  	var questionType = $("#questionType").val();
  	if( questionType == "select one" ) {
  		showChoices();
  	} else if( questionType == "select all that apply" ) {
  		showChoices();
  	} else {
  		removeChoices();
  	}

  });

});

function closeDialog() {
	$('#questionEditWindow').modal('hide'); 
}

function showChoices() {

	var choiceHTML = "<table class='table table-striped table-bordered'>"
	+ "<thead><tr><td colspan='3' style='background-color:#EEE;'>"
	+ "<h4><div class='pull-right'>"
	+ "<button type='button' onclick='addChoice()'"
	+ " id='addchoice' class='btn btn-small'>Add Choice</button>"
	+ "</div>Choices</h4></td></tr></thead><tbody id='choiceList'></tbody></table>";

	$("#choices").html(choiceHTML);
}

function removeChoices() {
	$("#choices").html("");
}

function addChoice() {

	var choiceNum = $("#choiceList tr").length;

	var html = "<tr id='choice" + choiceNum + "'>";
	html += "<td><input id='name' placeholder='Name' type='text'></td>";
	html += "<td><input id='label' placeholder='Label' type='text'></td>";
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

function okClicked() {

	if( validateQuestion() ) {
		var question = new Object();
		question.name = $("#questionName").val();
		question.label = $("#questionLabel").val();
		question.type = $("#questionType").val();
		
		//TODO: bind(constraint, relevant, required, readonly), 

		if( question.type == 'select one' || question.type == 'select all that apply' ) {
			var choices = document.getElementById("choiceList").getElementsByTagName("TR");
			var options = new Array();
			for( var index=0; index<choices.length; index++ ) {
				var option = new Object();
				var child = choices.item(index);
				var rows = child.getElementsByTagName('INPUT');
				alert(rows[0].value);
				option.name = rows[0].value;
				option.label = rows[1].value;
				options.push(option);
			}
			question.children = options;
		}

		//alert( JSON.stringify(question) );

		questionList.push(question);
		buildSurvey();
		reloadQuestionListHTML();
		closeDialog();
	}
}

function buildSurvey() {
	var survey = new Object();
	survey.children = questionList;
	var value = JSON.stringify(survey);
	$("#surveyjson").val(value);
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
	//TODO:
}

function getHTMLForQuestion(questionNum) {
	
	//TODO: add more question detail
	var question = questionList[questionNum];
	var html = "<tr id='question" + questionNum + "'>";
	html += '<td>Name:&nbsp;' + question.name + '</td>';
	html += "<td style='width:70px;text-align:center;'>" +
							"<a href='#' class='btn btn-small'>"+
							"	<i class='icon-pencil'></i> Edit"+
							"</a>"+
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

	//TODO:finish this
	//var html = '';

	//for( var question in questionList ) {
	//	html = html + getHTMLForQuestion(question);
	//}

	//alert(html);

	$("#questionList").append( getHTMLForQuestion( questionList.length-1) );
}


