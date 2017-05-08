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

    $('#login-form').submit(function (e) {
        e.preventDefault();
		
        var git_repo = document.getElementById("login-form")[1].value;
        var ip = document.getElementById("login-form")[0].value;
        console.log(git_repo);
        jQuery.ajax({
            type: "POST",
            url: "http://104.196.235.71/deployer/v1/" + ip + "/deploy",
            data: '{ "git_url": "' + git_repo + '"}',
            dataType: "json",
            contentType: "application/json",
            success: function (data, textStatus, jqXHR) {
                console.log(data.message);
                showOutput(data.message, textStatus);
            }, //function(data, textStatus, jqXHR)
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
            }
        });
        
    });

    function myFunction() {
        var ip = document.getElementById("login-form")[0].value;
        jQuery.ajax({
            type: "GET",
            url: "http://104.196.235.71/deployer/v1/" + ip + "/status",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                console.log(data + textStatus);
                document.getElementById("demo").innerHTML = data.message;
            }, //function(data, textStatus, jqXHR)
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
            }
        });
    }

    function showOutput(message, status) {
        var e = document.getElementById("output");
        e.style.display = 'block';
        document.getElementById("message").innerHTML = message;
        document.getElementById("status").innerHTML = status;
    }

    $(function () {

        $('a[href^="#"]').click(function (event) {
            var id = $(this).attr("href");
            var offset = 20;
            var target = $(id).offset().top - offset;

            $('html, body').animate({
                scrollTop: target
            }, 500);
            event.preventDefault();
        });

    });
    
    function getToken(code) {
        jQuery.ajax({
            type: "POST",
            url: "https://github.com/login/oauth/access_token",
            data: '{"code":'+ code + ',"client_id": "9ef838536d7516d3ab56","client_secret":"a6db61f6620ac50e96dd93193c02e753fb91d1ea"}',
            dataType: "json",
            contentType: "application/json",
            success: function (data, textStatus, jqXHR) {
                console.log(data);// this is access token
            }, //function(data, textStatus, jqXHR)
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
            }
        });
    }

});