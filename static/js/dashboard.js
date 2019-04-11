function get_faces(){
    $.ajax({
        type: "GET",
        url: "/get_faces",
        success: function(data) {
          console.log(data);
        },
        error: function(error) {
          console.log(error);
        }
  });
}