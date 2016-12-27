
// 用户登录
  function sign_in(url){
    var api = "/api/sign-in";
    if (url=="adm"){
        var api = "/api/adm/sign-in";
    }
    $('#flash').text('').hide();
     $(".form-control").attr('style','border-color:#cbd5dd;');
    var username = $("#username").val();
    var password = $("#password").val();
    var vercode = $("#vercode").val();
    var code_url = $("#code-url").val();
    var remember_me = $("#remember_me").val();
    if (!username){
        $('#flash').show();
        $('#flash').text('账号不能为空!');
        $('#username').attr('style','border-color:#800000;');
    }else if(!password){
        $('#flash').show();
        $('#flash').text('账号或密码错误!');
        $('#username').attr('style','border-color:#800000;');
        $('#password').attr('style','border-color:#800000;');
    }else{
        var next = getUrlParam('next')
        if(!next || next=="undefined" || next == null){
            next = "/"
        }
        $.post(api,
            {username:username, password:password, vercode:vercode, code_url:code_url, remember_me:remember_me},
            function(data,status){
                if(data.success){
                    window.location.href = next;
                }else if(data.flash && data.flash.type != "html"){
                    $('#flash').show();
                    $('#flash').text(data.flash.msg);
                }else if(data.flash && data.flash.type == "html"){
                    $('#flash').show();
                    $('#flash').append(data.flash.msg);
                }
                if(data.code){
                    $('#div-vercode').show();
                    $('#code-img').attr('src', '/static/'+data.code.url);
                    $('#code-url').val(data.code.url);
                }

         });
    }


  }

  // 用户注册
  function sign_up(){

    $('#flash').text('').hide();
    $(".form-control").attr('style','border-color:#cbd5dd;');
    var email = $("#email").val();
    var username = $("#username").val();
    var password = $("#password").val();
    var password2 = $("#password2").val();
    var vercode = $("#vercode").val();
    var code_url = $("#code-url").val();
    if (!email){
        $('#flash').show();
        $('#flash').text('邮箱不能为空!')
        $('#email').attr('style','border-color:#800000;');

    }else if(/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(email) == false){
        $('#flash').show();
        $('#flash').text('邮箱格式不正确')
        $('#email').attr('style','border-color:#800000;');
    }else if (!username){
        $('#flash').show();
        $('#flash').text('用户名不能为空!')
         $('#username').attr('style','border-color:#800000;');
    }else if(!password){
        $('#flash').show();
        $('#flash').text('密码不能为空!')
        $('#password').attr('style','border-color:#800000;')

    }else if(password != password2){
        $('#flash').show();
        $('#flash').text('两次密码不一致!')
        $('#password2').attr('style','border-color:#800000;')

    }else if(!vercode){
        $('#flash').show();
        $('#flash').text('验证码错误!')
        $('#vercode').attr('style','border-color:#800000;')
    }else{
        $.post('api/sign-up',
            {username:username, password:password, password2:password2,vercode:vercode, code_url:code_url, email:email},
            function(data,status){
                if(data.success){
                    window.location.href = "/sign-in";
                }else if(data.flash && data.flash.type != "html"){
                    $('#flash').show();
                    $('#flash').text(data.flash.msg);
                }else if(data.flash && data.flash.type == "html"){
                    $('#flash').show();
                    $('#flash').append(data.flash.msg);
                }
                if(data.code){
                    $('#code-img').attr('src', '/static/'+data.code.url);
                    $('#code-url').val(data.code.url);
                }

         });
    }
  }

  // 用户密码修改
  function reset_password(){

    $('#flash').text('').hide();
    $(".form-control").attr('style','border-color:#cbd5dd;');
    var old_password = $("#old_password").val();
    var aa = $("#old_password11").val();
    if (!old_password){
        old_password = "0"
    }
    var password = $("#password").val();
    var password2 = $("#password2").val();

    if(password != password2){
        $('#flash').show();
        $('#flash').text('两次密码不一致!')
        $('#password2').attr('style','border-color:#800000;');
    }else{
        $.post('/api/accounts/password-reset',
            {password:password, password2:password2, old_password:old_password},
            function(data,status){
                if(status = 'success'){
                    if(data.url){
                        window.location.href = data.url

                    }else if(data.flash && data.flash.type != "html"){
                        $('#flash').show();
                        $('#flash').text(data.flash.msg);
                    }else if(data.flash && data.flash.type == "html"){
                        $('#flash').show();
                        $('#flash').append(data.flash.msg);
                    }
                }

         });
    }
  }

  // 用户邮箱修改
  function change_email(){

    $('#flash').text('').hide();
    $(".form-control").attr('style','border-color:#cbd5dd;');
    var email = $("#email").val();
    var password = $("#password").val();
    var code_id = $("#code-id").val();
    var email_code = $("#email-code").val();

    if(!email){
        $('#flash').show();
        $('#flash').text('邮箱不能为空!')
        $('#email').attr('style','border-color:#800000;');
    }else if(/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(email) == false){
        $('#flash').show();
        $('#flash').text('邮箱格式不正确')
        $('#email').attr('style','border-color:#800000;');

    }else if (!password){
        $('#flash').show();
        $('#flash').text('密码错误!')
        $('#password').attr('style','border-color:#800000;');

    }else if(!email_code){
        $('#flash').show();
        $('#flash').text('验证码错误!')
        $('#email-code').attr('style','border-color:#800000;');
    }else{
        $.post('/api/accounts/email-change',
            {password:password, email:email, email_code:email_code, code_id:code_id},
            function(data,status){
                if(status = 'success'){
                    if(data.url){
                        window.location.href = data.url

                    }else if(data.flash && data.flash.type != "html"){
                        $('#flash').show();
                        $('#flash').text(data.flash.msg);
                    }else if(data.flash && data.flash.type == "html"){
                        $('#flash').show();
                        $('#flash').append(data.flash.msg);
                    }
                }

         });
    }
  }


  // 找回密码
  function ret_password(){

    $('#flash').text('').hide();
    $(".form-control").attr('style','border-color:#cbd5dd;');
    var email = $("#email").val();
    var password = $("#password").val();
    var password2 = $("#password2").val();
    var code_id = $("#code-id").val();
    var email_code = $("#email-code").val();

    if (!email){
        $('#flash').show();
        $('#flash').text('邮箱不能为空!')
        $('#email').attr('style','border-color:#800000;');

    }else if(/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(email) == false){
        $('#flash').show();
        $('#flash').text('邮箱格式不正确')
        $('#email').attr('style','border-color:#800000;');
    }else if(!password){
        $('#flash').show();
        $('#flash').text('密码不能为空!')
        $('#password').attr('style','border-color:#800000;')

    }else if(password != password2){
        $('#flash').show();
        $('#flash').text('两次密码不一致!')
        $('#password2').attr('style','border-color:#800000;')

    }else if(!email_code){
        $('#flash').show();
        $('#flash').text('邮件或短信验证码错误！')
        $('#email-code').attr('style','border-color:#800000;');
    }else{
        $.post('/api/accounts/retrieve-password',
            {password:password, password2:password2,　email_code:email_code, code_id:code_id, email:email},
            function(data,status){
                if(data.url){
                    window.location.href = data.url;
                }else if(data.flash && data.flash.type != "html"){
                    $('#flash').show();
                    $('#flash').text(data.flash.msg);
                }else if(data.flash && data.flash.type == "html"){
                    $('#flash').show();
                    $('#flash').append(data.flash.msg);
                }
                if(data.code){
                    $('#code-img').attr('src', '/static/'+data.code.url);
                    $('#code-url').val(data.code.url);
                }

         });
    }
  }

//  // 用户编辑
//  function edit_user_profile(){
//    $('#flash').text('').hide();
//    $(".form-control").attr('style','border-color:#cbd5dd;');
//    var username = $("#username").val();
//    var sex = $('input:radio:checked').val();
//    var p = $("#p option:selected").val();
//    var c = $("#c").val()
//    var a = $("#a").val()
//    var info = $("#info").val();
//    var avatar = $("#avatar").val();
//    alert(avatar);
//    if (!username){
//        $('#flash').show();
//        $('#flash').text('名号不能为空!')
//        $('#username').attr('style','border-color:#800000;');
//    }else{
//        $.post('/api/accounts/edit-profile',
//            {username:username, sex:sex, p:p, c:c, a:a, info:info, avatar:"" },
//            function(data,status){
//                if(data.url){
//                    window.location.href = data.url;
//                }else if(data.flash && data.flash.type != "html"){
//                    $('#flash').show();
//                    $('#flash').text(data.flash.msg);
//                }else if(data.flash && data.flash.type == "html"){
//                    $('#flash').show();
//                    $('#flash').append(data.flash.msg);
//                }
//                if(data.code){
//                    $('#code-img').attr('src', '/static/'+data.code.url);
//                    $('#code-url').val(data.code.url);
//                }
//
//         });
//    }
//
//}