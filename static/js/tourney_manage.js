// Some ajaxy stuff for submitting the form
$(document).ready(function() {
     // Handy function to toggle between two side-by-side <ul> elements
     // Accepts a ul element within a ul element, moves it over to the next one
     $.fn.listToggle = function() {
        
     };
    
	// Accepts the <li> containing the team's <form> and accepts or rejects them
	// Returns true if the ajax post succeeds
	// Returns the error message otherwise
	$.fn.ajaxPost = function() {
         $(this).addClass("ajax-loading");
	    var link = $(this).children('form');
	    // Get the form data to submit
   	    var data = link.serialize();
	    // Get the URL that the form submits it to
	    var postUrl = link.attr('action');
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
              		$('.ajax-loading').children('form').attr("action", $('.ajax-loading').parents('div').attr("data-post-url"));
                    	$('.ajax-loading').removeClass("ajax-loading").removeClass("loading");
                    	$('.ajax-loading').toggleClass("pending").toggleClass("accepted");
        		    } else {
          			$("#error").text("There was an error! " + html);
          			$("#error").fadeIn();
          			$("#error").click(function () {
          			    $(this).fadeOut();
          			}); 
        		    }
	      }
	    });
	    return returnString.value;
	};
	
    // from jquery ui - make the lists connected and sortable
	$("#pending_list, #accepted_list").sortable({
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
