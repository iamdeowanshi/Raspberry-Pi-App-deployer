
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
    
    $('#login-form').submit(function(e) {
        e.preventDefault();
        var git_repo = document.getElementById("login-form")[1].value;
        console.log(git_repo);
        jQuery.ajax({
         type: "POST",
         url: "http://104.196.235.71/deployer/v1/6e2edab7-69be-43d0-a304-e655a708b811/deploy",
         data: "{ git_url: git_repo}",
         dataType:"json",
         success: function(data, textStatus, jqXHR) {
            console.log(data + textStatus);
         }, //function(data, textStatus, jqXHR)
         error: function(jqXhr, textStatus, errorThrown) {
         console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
         }
        });
    });



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
