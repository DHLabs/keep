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
  fileselect = document.getElementById("fileselect");
  filedrag = document.getElementById("filedrag");
  fileselect.addEventListener("change", FileSelectHandler, false);
  filedrag.addEventListener("dragover", FileDragHover, false);
  filedrag.addEventListener("dragleave", FileDragHover, false);
  filedrag.addEventListener("drop", FileSelectHandler, false);
  console.log("hello");
});
