
function getQuestionOptions(select) {
	//TODO: more stuff

	//incidence, average value, etc.
	var html = 'Type:<select>';
	html += "<option value='incidence'>Incidence</option><option value='average'>Average</option>";
	html += '</select>';

	var tds = select.parentNode.parentNode.getElementsByTagName("td");
	tds.item(2).innerHTML = html;
}

function submitReport() {

	var reports = new Array();

	var items = document.getElementById( 'reportItems' ).getElementsByTagName( 'tr' );
	//alert( items );
	for( var i=0; i<items.length; i++ ) {
		var inputs = items.item(i).getElementsByTagName('select');
		//alert(inputs);
		if( inputs.length == 3 ) {
			var report = new Object();

			report.form_id = inputs.item(0).value.split(':')[0];
			report.form_name = inputs.item(0).value.split(':')[1];
			report.form_question = inputs.item(1).value;
			report.report_type = inputs.item(2).value;

			reports.push( report );
		}
	}

	var json = JSON.stringify( reports )
	//alert( json );
	$("#id_report_json").val( json );

	return true;
}

function getRepoOptions() {

	var select = "<select onchange='showRepoQuestions(this)'>\n";

	for( var i in repos ) {
		select += "<option value='" + repos[i].mongo_id + ":" + repos[i].name + "'>";
		select += repos[i].name + "</option>\n";
	}

	select += '</select>\n';

	return select;
}

function showRepoQuestions(select) {

	//get list of all questions
	var questionList = new Array();
	buildQuestionList( questionList, repos[select.selectedIndex].children );

	var html = 'Term:<select onchange="getQuestionOptions(this)">';

	for( var i=0; i<questionList.length; i++ ) {
		html += '<option>' + questionList[i].name + "</option>";
	}

	html += '</select>';

	var tds = select.parentNode.parentNode.getElementsByTagName("td");
	tds.item(1).innerHTML = html;
}

function buildQuestionList( questionList, formChildren )  {

	for( var i=0; i<formChildren.length; i++ ) {
		var question = formChildren[i];
		if( question.type == 'group' ) {
			buildQuestionList( questionList, question.children );
		} else {
			questionList.push( question );
		}
	}
}

function addItem() {

	var html = '<tr><td> Repo:' + getRepoOptions()
		+'</td><td></td><td></td>';
	html += "<td style='width:40px;text-align:center;'>"+
							"<button type='button' onclick='deleteItem(this)'"
								+" class='btn btn-danger'>"+
							 "   <i class='icon-trash'></i>"+
							"</button>"+
						"</td>"
	html += '</tr>';

	$("#reportItems").append(html);

	var items = document.getElementById('reportItems').getElementsByTagName('tr');
	showRepoQuestions( items.item( items.length - 1 ).getElementsByTagName('select').item(0) );
}

function deleteItem(deleteButton) {
	
	var tr = deleteButton.parentNode.parentNode;

	tr.parentNode.removeChild( tr );
}

function buildReportItems() {
	//TODO: finish this
}