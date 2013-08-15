function FileDragHover(e) {
    e.stopPropagation();
    e.preventDefault();
    e.target.className = (e.type == "dragover" ? "hover" : "");
  }

  // file selection
  function FileSelectHandler(e) {

    // cancel event and hover styling
    FileDragHover(e);

    // fetch FileList object
    var files = e.target.files || e.dataTransfer.files;

    var fileseelct = document.getElementById( "fileselect" );
    $("input[name=name]").val( files[0].name.split(".")[0] );
    fileseelct.files = files;
    $("#newform").submit();

  }

$(function() {
  var filedrag, fileselect;
  $.getJSON('/api/v1/data/', {
    'user': $('#user').html()
  }, function(data) {
    var datum, feed_tmpl, info, label, _i, _len, _ref, _results;
    console.log(moment().format());
    $('#submissions_feed').html('');
    if (data.length === 0) {
      return $('#submissions_feed').html('<div style="color:#AAA;">No submissions yet =[</div>');
    } else {
      feed_tmpl = _.template($('#submission_feed_tmpl').html());
      _ref = data.objects;
      _results = [];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        datum = _ref[_i];
        label = 'Submission from ';
        if (datum.uuid) {
          label += 'mobile device';
        } else {
          label += 'web';
        }
        info = {
          label: label,
          time: moment.utc(datum.timestamp).fromNow(),
          link: ("/api/v1/data/" + datum.repo_id + "?user=") + $('#user').html(),
          survey_name: datum.survey_label ? datum.survey_label : datum.repo
        };
        _results.push($('#submissions_feed').append(feed_tmpl(info)));
      }
      return _results;
    }
  });
  fileselect = document.getElementById("fileselect");
  filedrag = document.getElementById("filedrag");
  fileselect.addEventListener("change", FileSelectHandler, false);
  filedrag.addEventListener("dragover", FileDragHover, false);
  filedrag.addEventListener("dragleave", FileDragHover, false);
  filedrag.addEventListener("drop", FileSelectHandler, false);
  console.log("hello");
});
