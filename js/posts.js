$(document).ready(
  $("h4").append(function () {
      $.ajax({
          url: "http://127.0.0.1:5000/check",
          type: "application/json",
          method : "GET",
          success: function (result) {
              for (i=0; i<result["name"].length;i++){
                  console.log(result["name"][i])
                  $("#divdo").append(result["name"][i]);
              }
                  
                  
          
          },
         
    
      }
  );
     
  


  
}))

