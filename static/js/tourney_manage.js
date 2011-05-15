// Some ajaxy stuff for submitting the form
$(document).ready(function() {
	// Accepts the <li> containing the team's <form> and accepts or rejects them
	// Returns true if the ajax post succeeds
	// Returns the error message otherwise
	$.fn.ajaxPost = function() {
	    var accept = "{% url sc2tournament.views.tournament_accept %}";
	    var reject = "{% url sc2tournament.views.tournament_reject %}";
	    var link = $(this).children('form');
	    // Get the form data to submit
	    var data = link.serialize();
	    // Get the URL that the form submits it to
	    var postUrl = link.attr('action');
	    // Conditional stuff to consolidate accepted/rejected into one function
	    var accepted = postUrl == accept;
	    if(accepted) console.log("Called with an accept url");
	    var newUrl = accepted ? reject : accept;
	    var appendClass = accepted ? "#accepted_teams" : "#pending_teams";
	    // Allow pass-by-reference for the success section of the ajax request
	    function returnObj() {
		this.value = -1;
	    }
	    var returnString = new returnObj();
	    $.ajax({
              // AJAX request to the URL the form was going to submit to
              url: postUrl, 
              // Post ... 
              type: "POST",
              //pass the data         
              data: data,     
              //Do not cache the page
              cache: false,
              //success
              success: function(html) {
		    // error checking
		    if (html.indexOf('<html>') != -1) {
			console.log($(html).text());
		    } else {
			$("#error").text("There was an error! " + response +  " (click to close) ");
			$("#error").fadeIn();
			$("#error").click(function () {
			    $(this).fadeOut();
			}); 
		    }
	      }
	    });
	    return returnString.value;
	};
	
	$.fn.ajaxToggle = function() {
	  var team = this;
          console.log("Called with " + team);
          var accept = "{% url sc2tournament.views.tournament_accept %}";
          var reject = "{% url sc2tournament.views.tournament_reject %}";
          // Get the parent - i.e., the form element, this function is called from <a>
          var link = $(team).parent();
          // Get the form data to submit
          var data = link.serialize();
          // Get the URL that the form submits it to
          var postUrl = link.attr('action');
          // Conditional stuff to consolidate accepted/rejected into one function
          var accepted = postUrl == accept;
          if(accepted) console.log("Called with an accept url");
          var newUrl = accepted ? reject : accept;
          var appendClass = accepted ? "#accepted_teams" : "#pending_teams";
          console.log("Posting to " + postUrl);
          $.ajax({
              // AJAX request to the URL the form was going to submit to
              url: postUrl, 
              // Post ... 
              type: "POST",
              //pass the data         
              data: data,     
              //Do not cache the page
              cache: false,
              //success
              success: function (html) {              
                  // TODO: we can check the result here
                  if ( html.indexOf('<html>') != -1 ) {
                      // Move up to the <li> tag
                      link = link.parent();
                      // Fade it out, move it to accepted teams, fade in.              
                      link.fadeOut(100, function() {      
                        link.remove();
			link.appendTo(appendClass + " ul:first ");
                        link.fadeIn(100, function() {       
                          $(this).children('form').attr('action', newUrl);
                         // TODO: Methinks there's a more efficient way to do this
			             $('.pending , .accepted').unbind('click');
			             $('.pending , .accepted').click(function() { $(this).ajaxToggle() });
                        });
                      });
                  } else { // Deal with an ajax error
			$("#error").text("There was an error! " +html+ " (click to close) ");
			$("#error").fadeIn();
			$("#error").click(function () {
				$(this).fadeOut();
			});
		   }
		    
              }
          });
	  return -1;
        };
	
	// add the listeners
        //$('.pending , .accepted').click(function() { $(this).ajaxToggle() });
	
	// from jquery ui
	$( "#pending_list" ).sortable({
		connectWith: "ul"
	});
	$("#accepted_list").sortable({
		connectWith: "ul"
	});
	
	// Trying to do some stuff with sortable ...
	$("#pending_list , #accepted_list").sortable({
	    receive: function(event, ui) { 
		// TODO: find the element, give it an ajax spinny thing,
		// run the ajax request, and if it fails, put it back in the
		// other div and display a message
		var response = ui.item.ajaxPost();
		$(ui.item).addClass("loading");
	    }
	});
});
