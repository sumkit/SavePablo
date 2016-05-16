function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

//Credit to http://stackoverflow.com/questions/9461621/how-to-format-a-number-as-2-5k-if-a-thousand-or-more-otherwise-900-in-javascrip
function nFormatter(num) {
     if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B';
     }
     if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
     }
     if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
     }
     return num;
}
function updateMPS(num){
  var t = document.getElementById('mps'); 
  t.innerHTML = nFormatter(num);
}
function updateMoney(num){
  var t = document.getElementById('money');
  t.innerHTML = nFormatter(num);
} 

//Updates count,cost elements of an image elem
function updateView(elem,count,cost){
  //Get corresponding fields
  var par = elem.parentNode.parentNode;
  var p = par.querySelector(".text");
  var oC = p.querySelector("#owned");
  var pC = p.querySelector("#price");
  //update final values shown 
  oC.innerHTML = nFormatter(count);
  pC.innerHTML = nFormatter(cost);

}

function updateLeaderboard() {

  $.ajax({
    url: "/savepablo/getBoard",
    type: "GET",
    datatype:"json",

    success:function(state){
      $("ol#board").empty();
      for(var i = 0; i < state.players.length; i++){
        var t = state.players[i];
        $("ol#board").append("<li>"+t+"</li>");
      }
    },
    error: function(xhr, textStatus, errorThrown){
       console.log(textStatus+ ' - request failed: '+errorThrown);
    }

  });
}

function updateFam() {
  $.ajax({
    url: "/savepablo/getFam",
    type: "GET",
    datatype:"json",
    success:function(state){
      $("#fam").empty();
      for(var i = 0; i < state.names.length; i++){
        var n = state.names[i];
        var id = state.ids[i];

        var outsideDiv = document.createElement('div');
        outsideDiv.style='padding-bottom: 10px';

        var div=document.createElement('div');
        div.class = "btn-group btn-group-xs";
        div.role='group';
        div.style='padding-left:60px';

        var a = document.createElement('a');
        a.href = "/savepablo/link2/id"
        a.innerHTML=n;

        var button = document.createElement('a');
        button.href = "/savepablo/unfriend/"+id
        button.class ="btn btn-primary btn-lg active";
        button.innerHTML = "Unfriend";

        div.appendChild(button);
        outsideDiv.appendChild(a);
        outsideDiv.appendChild(div);
        $("#fam").append(outsideDiv);
      }
    },
    error: function(xhr, textStatus, errorThrown){
       console.log(textStatus+ ' - request failed: '+errorThrown);
    }
  });
}

//Sends ajax request to server, to update money every second
function updateGame(){
    $.ajax({
    url: "/savepablo/step",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "POST",
    datatype:"json",

    success:function(state){
      if(state['won'] == 'True' && won < 1){
         window.location.replace("/savepablo/congrats");
      }

      updateMoney(state['money']);
     }

    });
}

$(document).ready(function(){

  //Load the game state from server
  $.ajax({
    url: "/savepablo/load",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "GET",
    datatype:"json",

    success:function(state){
      updateLeaderboard();
      updateFam();

      for(var i = 0; i < state.length; i++){
        var obj = state[i];
        var type = obj['model']
        if(type == 'savepablo.item'){
          var fields = obj['fields'];
          var id = fields['name'];
          var count = fields['count'];
          var cost = fields['cost'];
          var elem = document.getElementById(id);
          updateView(elem,count,cost);
        }
        if(type == 'savepablo.myuser'){
          var fields = obj['fields'];
          var money = fields['points'];
          var mps = fields['mps'];
          updateMoney(money);
          updateMPS(mps);
        }
      }
    }
  });


  /* Sends request to server, which takes care of game logic when clicking
   * on Kanye */ 
  $("#kanye").click(function() {
    $.ajax({
    url: "/savepablo/click",
    
    data:{csrfmiddlewaretoken: getCSRFToken()},
    type: "POST",
    datatype:"text/plain", 

    success: function(money){
      updateMoney(money);
    }
         
  });
  });

  /* Handles logic when items is bought*/
  $('.image').not('#kanye').click(function(event){

    var hoverElem = event.target;
    var id = hoverElem.id;

    $.ajax({
      url: "/savepablo/bought",
      
      data:{csrfmiddlewaretoken: getCSRFToken(),
            id : id},
      type: "POST",
      datatype:"json", 

      success: function(data){
        // Not enough money to buy
        if(data.length == 0){
          alert("Not enough money");
          console.log('not enough money');
        }
        //Update frontend to match server data
        else{
          //Parse data from json
          var count = data['count'];
          var cost = data['cost'];
          var mps = data['mps'];
          var money = data['money'];
          //find correct element to modify 
          var hoverElem = event.target;
          //update final values shown 
          updateMPS(mps);
          updateMoney(money);
          updateView(hoverElem,count,cost)

        }
      }
    });
  });
});


setInterval(updateGame,1000)
setInterval(updateLeaderboard, 1000)
setInterval(updateFam, 2000)
