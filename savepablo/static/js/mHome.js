function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}
//bool that stores if we should should still search
var keepSearching = false;

function sendReadyBegin(){
    $.ajax({
    url: "/savepablo/ready",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "POST",
    datatype:"text/plain",

    success:function(state){
      //Load the game
      setTimeout(function(){window.location.href = "/savepablo/game"}
                  ,3500); 
     },

    error:function(state){
      //We recieve an error if we cannot find a match
      //We can simply call the function again until we get a success
      setTimeout(sendReadyBegin,500);
    }

    })

}
function pingServer(){
    if(keepSearching){
      $.ajax({
      url: "/savepablo/queue",

      data:{csrfmiddlewaretoken: getCSRFToken()},

      type: "POST",
      datatype:"text/plain",

      success:function(state){
        sendReadyBegin(); 
       },

      error:function(state){
        //We recieve an error if we cannot find a match
        //We can simply call the function again until we get a success
        setTimeout(pingServer,1500);
        
      }

      })
    }
}

function pingServer2(){
    if(keepSearching){
      $.ajax({
      url: "/savepablo/wait_accept",


      type: "GET",
      datatype:"text/plain",

      success:function(state){
       window.location.href = "/savepablo/launch"; 
       },

      error:function(state){
        //We recieve an error if we cannot find a match
        //We can simply call the function again until we get a success
        setTimeout(pingServer2,500);
        
      }

      })
    }
}


$(document).ready(function(){
  $('#quote').slideDown(1500);
  if($('#inv').text() == "yes"){
    keepSearching = true; 
    $('#invite').hide();
    $('#game').hide();
    $('#cancel2').show();
    $('#spinner').show();
    $('#wait').show();
    $('#search').hide();
    $('#share').hide();
    $('#link').hide();
    $('#quote').hide();
    pingServer2();
    //Wait for accept
  }

  $('#cancel').click(function(event){
    $.ajax({
    url: "/savepablo/cancel",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "POST",
    datatype:"text/plain",

    success:function(state){
      keepSearching = false; 
      $('#game').show()
      $('#invite').show()
      $('#cancel').hide()
      $('#spinner').hide()
      $('#share').hide()
      $('#link').hide()
      $('#quote').slideDown(1500);

     },
    })
  });
  $('#cancel2').click(function(event){
    $.ajax({
    url: "/savepablo/cancel2",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "POST",
    datatype:"text/plain",

    success:function(state){
      keepSearching = false; 
      $('#game').show()
      $('#invite').show()
      $('#cancel2').hide()
      $('#spinner').hide()
      $('#share').hide()
      $('#link').hide()
      $('#quote').slideDown(1500);

     },
    })
  });


  $('#invite').click(function(event){
   keepSearching = true; 
   $.ajax({
    url: "/savepablo/link",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "POST",
    datatype:"text/plain",

    success:function(state){
      $('#game').hide();
      $('#invite').hide();
      $('#cancel2').show();
      $('#spinner').show();
      $('#wait').show();
      $('#search').hide();
      $('#share').show();
      $('#link').show();
      $('#link').html(state);
      $('#quote').hide();

      pingServer2();
     },
    })
    //Wait for accept
  });

  $('#game').click(function(event){
    keepSearching = true; 
     //Hide find game buttons, show spinner,cancel button
    $('#game').hide();
    $('#invite').hide();
    $('#cancel').show();
    $('#spinner').show();
    $('#search').show();
    $('#wait').hide()
    $('#quote').hide();

    //Find game
    pingServer();
    });
});
