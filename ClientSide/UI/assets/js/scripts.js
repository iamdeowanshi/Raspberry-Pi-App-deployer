
jQuery(document).ready(function() {
	
    /*
        Fullscreen background
    */
    $.backstretch("assets/img/backgrounds/1.jpg");
    
    /*
        Form validation
    */
/*    $('.login-form input[type="text"], .login-form input[type="password"], .login-form textarea').on('focus', function() {
    	$(this).removeClass('input-error');
    });*/
	//https://github.com/amitakamat/cmpe273
    
	
    $('#login-form').submit(function(e) {
        e.preventDefault();
		var username=prompt("Github Username:");
		var passwordval=prompt("Github Password:");
        var git_repo = document.getElementById("login-form")[1].value;
        //console.log(git_repo);
		var gitusername=git_repo.split("/")
		jQuery.ajax({
         type: "GET",
         url: 'https://api.github.com/repos/' + gitusername[3] + "/" + gitusername[4] + '/hooks',
         //data: '{"name": "web","active": true,"events": ["push","pull_request"],"config": {"url": "http://104.196.235.71/payload","content_type": "json"}}',
         dataType:"json",
		headers: {
    "Authorization": "Basic " + btoa(username + ":" + passwordval)
  },
         success: function(data, textStatus, jqXHR) {
			 console.log(data.length);
				if(data.length>0)
				{
					ajaxcall3(gitusername,git_repo);
				}
				else
				{
					ajaxcall2(gitusername,git_repo,username,passwordval);
				}
            }, //function(data, textStatus, jqXHR)
         error: function(jqXhr, textStatus, errorThrown) {
         console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
         }
        });
        
    });
	
	function ajaxcall2(gitusername,git_repo,username,passwordval)
	{
		jQuery.ajax({
         type: "POST",
         url: 'https://api.github.com/repos/' + gitusername[3] + "/" + gitusername[4] + '/hooks',
         data: '{"name": "web","active": true,"events": ["push","pull_request"],"config": {"url": "http://104.196.235.71/payload","content_type": "json"}}',
         dataType:"json",
		 headers: {
    "Authorization": "Basic " + btoa(username + ":" + passwordval)
  },
         success: function(data, textStatus, jqXHR) {
			 console.log(data);
					ajaxcall3(gitusername,git_repo);
            }, //function(data, textStatus, jqXHR)
         error: function(jqXhr, textStatus, errorThrown) {
         console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
         }
        });
	}
	function ajaxcall3(gitusername,git_repo)
	{
		//var data='{ "git_url":"'+git_repo+ '"}';
		//console.log(data);
		jQuery.ajax({
         type: "POST",
         url: "http://104.196.235.71/deployer/v1/6e2edab7-69be-43d0-a304-e655a708b811/deploy",
         data: '{ "git_url":"'+  git_repo +'"}',
         dataType:"json",
		 
         success: function(data, textStatus, jqXHR) {
            console.log(data + textStatus);         
            }, //function(data, textStatus, jqXHR)
         error: function(jqXhr, textStatus, errorThrown) {
         console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
         }
        });
	}



$(function () {

$('a[href^="#"]').click(function(event) {
var id = $(this).attr("href");
var offset = 20;
var target = $(id).offset().top - offset;

$('html, body').animate({scrollTop:target}, 500);
event.preventDefault();
});

});
    
});
