function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

var updateID,gameID; 

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

  //player reached $53 million!
  if(num >= 53000000) {
    window.location.replace("/savepablo/congrats");
  }
} 

function set_oMps(num){
  var t = document.getElementById('oMps'); 
  t.innerHTML = nFormatter(num);
}
function set_oMoney(num){
  var t = document.getElementById('oMoney');
  t.innerHTML = nFormatter(num);

  //opponent reached $53 million
  if(num >= 53000000) {
    window.location.replace("/savepablo/lose")
  }
} 
function set_username(name){
  var t = document.getElementById('small');
  t.innerHTML = name;
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
//Update only cost element of an image elem, used for right column
function updateCost(elem,cost){
  //Get corresponding fields
  var par = elem.parentNode.parentNode;
  var p = par.querySelector(".text");
  var pC = p.querySelector("#price");
  //update final values shown 
  pC.innerHTML = nFormatter(cost);
}

//Disables all clicking for 30 seconds
function disableClicking(){
  clearInterval(updateID);
  clearInterval(oppID);
  var block = document.createElement('div')
  block.id = 'cover'
  block.style.backgroundColor = "#ff0000";
  block.style.bottom = '0';
  block.style.left = '0';
  block.style.position = 'fixed';
  block.style.right = '0';
  block.style.top = '0';
  $('body').append(block);
  $('#cover').css('opacity','0.2');
  //reset intervals after 30 seconds
  setTimeout(function(){
    $('#cover').remove();
    updateID = setInterval(updateGame,1000);
    gameID = setInterval(getOpp,1000);
  
  },30000);
}
//Appends message to alerts
function appendMessage(message,id){
   var div = document.createElement('div');
   var a = document.createElement('a');
   var p = document.createElement('p');
   a.innerHTML = "&times";
   a.className = "close";
   a.setAttribute('data-dismiss','alert');
   a.setAttribute('aria-label','close');
   div.className = "alert alert-danger";
   div.appendChild(a);
   p.innerHTML = message  
   div.appendChild(p);
   $(id).empty();
   $(id).append(div);
}
//Sends ajax request to server, to update money every second
function updateGame(){
    $.ajax({
    url: "/savepablo/mstep",

    data:{csrfmiddlewaretoken: getCSRFToken()},

    type: "POST",
    datatype:"json",

    success:function(state){
      updateMoney(state['money']);
      if(state['first'] == '1'){
        $('#hold2').empty();
        appendMessage("You lost money!","#hold2")
      }
      if(state['second'] == '1'){
        $('#hold2').empty();
        appendMessage("You lost MPS!","#hold2")
      }
      if(state['third'] == '1'){
        $('#hold2').empty();
        appendMessage("Your money got stolen!","#hold2") 
      }

     },
    error:function(state){
      if(state.responseText == 'canClick'){
        disableClicking();  
      }
    }
    })
}
function getOpp(){
    $.ajax({
    url: "/savepablo/getopp",

    type: "GET",
    datatype:"json",

    success:function(state){
        fields = state[0]['fields']
        money = fields['mPoints']
        mps = fields['mMps']
        fields1 = state[1]['fields']
        username = fields1['username']
        set_oMps(mps)
        set_oMoney(money)
     }

    })

}
function applyCooldown(cd,id){
  console.log(cd + " " + cd);

  $('#' + id).hide(100,function(){
    $('#' + id).fadeIn(cd * 1000); 
  }); 
  



}
$(document).ready(function(){

  //Sends ajax request to remove Games with the user as a player. 
  $(window).unload(function(){
    $.ajax({
      type: 'POST',
      //false, since ajax request may be cancelled if window is unloaded
      async: false,
      url: '/savepablo/unload',
      data:{csrfmiddlewaretoken: getCSRFToken()},
      success: function(test){

      } 
    })
  
  })
  /* Sends request to server, which takes care of game logic when clicking
   * on Kanye */ 
  $("#kanye").click(function() {
    $.ajax({
    url: "/savepablo/mclick",
    
    data:{csrfmiddlewaretoken: getCSRFToken()},
    type: "POST",
    datatype:"text/plain", 

    success: function(money){
      updateMoney(money);
    }
         
  })
  });

  /* Handles logic when items is bought*/
  $('.image').not('#kanye').click(function(event){

    var hoverElem = event.target;
    var id = hoverElem.id;

    $.ajax({
      url: "/savepablo/mbought",
      
      data:{csrfmiddlewaretoken: getCSRFToken(),
            id : id},
      type: "POST",
      datatype:"json", 

      success: function(data){
        $('#hold').empty(); //Remove any messages
        //Reset images to original
        //Necesary since the images may be pirate bay from the debuff
        var elem = document.getElementsByClassName('image');
        if(elem[0].src.indexOf('/static/img/pirate-bay.jpg') != -1 ){
              elem[0].src = '/static/img/yeezys.jpg'
              elem[1].src = '/static/img/kim k.jpg'
              elem[2].src = '/static/img/tidal.jpg'
              elem[3].src = '/static/img/gofundme.png'
              elem[4].src = '/static/img/mark z .jpg'
        }
        // Not enough money to buy
        if(data.length == 0){
          console.log('not enough money')
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
          updateView(hoverElem,count,cost);
        }
       },
        error: function(msg){
          console.log(msg.responseText)
          var strings = msg.responseText.split(" ");
          console.log(strings);
          //If error is due to debuff
          if(strings[0] == 'debuff'){
              //Set each picture in store to pirate
              var elem = document.getElementsByClassName('image');
              for(i=0; i < elem.length;i++){
                  var e = elem[i];
                  e.src = '/static/img/pirate-bay.jpg';
              }
              //Show message indicating how many seconds left off debuff
              var mess ='You\'re items have been disabled for ' + strings[1] + ' more seconds!';
              appendMessage(mess,'#hold'); 
          }

        }
    })
  });
  /* Handles logic when debuff is bought*/
  $('.debuff').click(function(event){

    var hoverElem = event.target;
    var id = hoverElem.id;
    //Prevent clicking on image while on cooldown
    if($('#'+id).is(':animated')){
      return; 
    }
    $.ajax({
      url: "/savepablo/debuff",
      
      data:{csrfmiddlewaretoken: getCSRFToken(),
            id : id},
      type: "POST",
      datatype:"json", 

      success: function(data){
          if(data.length == 0){
            console.log("not enough money");
            console.log(id);
          }
          else{
          //Parse data from json
          var cost = data['cost'];
          var money = data['money'];
          var cd = data['cd'];
          //find correct element to modify 
          var hoverElem = event.target;
          //update final values shown 
          updateMoney(money);
          updateCost(hoverElem,cost);
          applyCooldown(cd,id)
          }
        }
      })
    })

});
//Temporary interval times for now, may need to decrease time
updateID = setInterval(updateGame,1000);
oppID = setInterval(getOpp,1000);
