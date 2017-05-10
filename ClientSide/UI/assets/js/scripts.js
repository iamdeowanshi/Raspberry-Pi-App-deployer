var code = "";
jQuery(document).ready(function () {


    $('.message a').click(function () {
        console.log("Inside this script");
        $('#output').hide();
        $('form').animate({
            height: "toggle",
            opacity: "toggle"
        }, "slow");
    });

    $(window).load(function () {
        var code = getAccessCode();
        if (code != "") {

        } else {
            alertModal();
        }
    })

    function getAccessCode() {
        var field = 'code';
        var url = window.location.href;
        if (url.indexOf('?' + field + '=') != -1)
            return url.split("code=")[1];
        else
            return "";
    }
    /*
        Fullscreen background
    */
    $.backstretch("assets/img/backgrounds/1.jpg");

    /*
        Form validation
    */
    $('.login-form input[type="text"], .login-form input[type="password"], .login-form textarea').on('focus', function () {
        $(this).removeClass('input-error');
    });

    $('#login-form').submit(function (e) {
        e.preventDefault();
        if (checkToken()) {
            alertModal();
            return;
        }

        $(this).find('input[type="text"], input[type="password"], textarea').each(function () {
            if ($(this).val() == "") {
                e.preventDefault();
                $(this).addClass('input-error');
                return;
            } else {
                $(this).removeClass('input-error');
            }
        });

        var git_repo = document.getElementById("login-form")[1].value;
        var ip = document.getElementById("login-form")[0].value;
        console.log(git_repo);
        jQuery.ajax({
            type: "POST",
            url: "https://104.196.235.71/deployer/v1/" + ip + "/deploy",
            data: '{ "git_url": "' + git_repo + '","code":"' + code + '","type": "web"}',
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
    $('#login-form1').submit(function (e) {
        e.preventDefault();
        myFunction1();
    });

    function myFunction1() {
        var ip = document.getElementById("login-form1")[0].value;
        jQuery.ajax({
            type: "GET",
            url: "https://104.196.235.71/deployer/v1/" + ip + "/status",
            dataType: "json",
            success: function (data, textStatus, jqXHR) {
                console.log(data + textStatus);
                $('#output').show();
                var message = "";
                list.forEach(function (element) {
                    message += "<b>Repo Url</b> :" + element.url +
                        "--> <b>Status</b> : " + element.status + "<br>";
                }, this);
                document.getElementById("result").innerHTML = message;
                document.getElementById("status").innerHTML = "Status: " +
                    textStatus;
            }, //function(data, textStatus, jqXHR)
            error: function (jqXhr, textStatus, errorThrown) {
                console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
            }
        });
    }

    function checkToken() {
        code = getAccessCode();
        return (code != "") ? false : true;
    }

    function alertModal() {
        $(document).ready(function () {
            jQuery('#message').html('<div class="alert alert-warning show" id="alert"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><strong>Info!</strong> You should <a href="https://github.com/login/oauth/authorize?client_id=9ef838536d7516d3ab56&scope=write:repo_hook"class="alert-link">Connect through Github</a></div>');
        });
        //document.getElementById("#message").style.display = "block";
    }

    function showOutput(message, status) {
        var e = document.getElementById("output");
        e.style.display = 'block';
        document.getElementById("result").innerHTML = message;
        document.getElementById("status").innerHTML = "Status: " + status;
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

    // function getToken(code) {
    //     json_data = '{"code":"' + code + '","client_id": "9ef838536d7516d3ab56","client_secret":"a6db61f6620ac50e96dd93193c02e753fb91d1ea"}';
    //     console.log(json_data);
    //     var xhr = jQuery.ajax({
    //         type: "post",
    //         url: "https://github.com/login/oauth/access_token",
    //         data: json_data,
    //         dataType: "json",
    //         contentType: "application/json",
    //         success: function (data, textStatus, jqXHR) {
    //             accessToken = data;
    //             console.log(data); // this is access token
    //         }, //function(data, textStatus, jqXHR)
    //         error: function (jqXhr, textStatus, errorThrown) {
    //             console.log(errorThrown); //function(jqXHR, textStatus, errorThrown)
    //         }
    //     });
    //     console.log(xhr);
    // }

});