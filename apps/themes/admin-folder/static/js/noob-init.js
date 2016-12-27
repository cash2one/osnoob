
//-------------------------------------------------------
$(document).ready(function(){

    //home show
     $('.carousel').carousel({
        interval: 4000
    });
    $('.carousel').carousel('cycle');

    //时间处理
    $('[unix-time]').each(function()
    {
        var time = parseInt($(this).attr('value'));
        var _time = time*1000;//事物时间戳
        var d　=　new Date(_time);　//事物日期
        var n_day = new Date()　//现在日期
        var timestamp = Date.parse(n_day);//现在时间戳
        var d_num = timestamp-_time //差时

        if (d_num < 60000){
            $(this).text('刚刚');

        }else if(d_num > 60000 && d_num <= 3600000){
            var _min = parseInt(d_num/60000);
            $(this).text(_min+'分钟前');

        }else if(d_num > 3600000 && d_num <= 86400000){
            var _h = parseInt(d_num/(3600000));
            var _min = parseInt((d_num%(3600000))/60000);
            $(this).text(_h+'小时'+_min+"分钟前");

        }else if(d_num > 86400000 && d_num <= 86400000*10){
            var _d = parseInt(d_num/86400000);
            var _h = parseInt((d_num%86400000)/3600000);
            $(this).text(_d+'天'+_h+"小时前");

        }else if(d_num > 86400000*10 && d.getFullYear()==n_day.getFullYear()){
            var dat = '';
            var year= d.getFullYear();
            var mon = d.getMonth()+1;
            //if (mon < 10){
            //    mon = '0'+mon;
            //}
            var day = d.getDate();
            var h =d.getHours();
            if (h < 10){
                h = "0"+h
            }
            var min=d.getMinutes();
            if (min < 10){
                min = "0"+min
            }
            dat = mon + '月' + day + '号 ' + h + ':' + min;
            $(this).text(dat);


        }else{
            var dat = '';
            var year= d.getFullYear();
            var mon = d.getMonth()+1;
            if (mon < 10){
                mon = '0'+mon;
            }
            var day = d.getDate();
            var h =d.getHours();
            if (h < 10){
                h = "0"+h
            }
            var min=d.getMinutes();
            if (min < 10){
                min = "0"+min
            }
            dat = year + '-' + mon + '-' + day + ' ' + h + ':' + min;
            $(this).text(dat);
          }

    });
    //checkCookie();

    //文章图片等比缩放
     var w = $(".blog-post").width();//容器宽度
     $(".img-post-ud").each(function(){

         //如果有很多图片，我们可以使用each()遍历
         var img_w = $(this).attr('width');//图片宽度
         var img_h = $(this).height();//图片高度
         if(img_w>w){
            //如果图片宽度超出容器宽度--要撑破了
            var height = (w/img_w)*img_h; //高度等比缩放
            $(this).css({"width":w,"height":height});
         //设置缩放后的宽度和高度
        }
     });
    add_pageview();

});

// 获取验证码
function get_vercode(){
    $.get("/api/get-vercode",function(data,status){
       var url = '/static/'+data.url;
        $("#code-img").attr("src", url);
        $("#code-url").attr("value", data.url);
    });
}

// 获取邮件验证码
function get_email_code(){
     $('#flash').text('').hide();
    var useremail = $("#email").val()
    if(useremail){
        $.post("/api/get-email-code",{email:useremail},function(data,status){
            var _id = data._id;
            $("#code-id").attr("value", _id);

            var count = 60;
            var countdown = setInterval(CountDown, 1000);
            function CountDown() {
                $("#send-email").attr("disabled", true);
                $("#send-email").val(count + "s 后重发");
                if (count == 0) {
                    $("#send-email").val("重新发送").removeAttr("disabled");
                    clearInterval(countdown);
                }
                count--;
            }
           });
    }else{
        $('#flash').text('请填入新邮箱！');

    }
}

// 获取邮件验证码
function get_email_code_ps(){
     $('#flash').text('').hide();
     $(".form-control").attr('style','border-color:#cbd5dd;')
    var email = $("#email").val()
    var img_code = $("#vercode").val()
    var code_url = $("#code-url").val()
    if(!email){
        $('#flash').text('请输入账户邮件').show();
        $('#email').attr('style','border-color:#800000;');
    }else{
        $.post("/api/get-email-code/ps",{email:email, vercode:img_code, vercode_url:code_url },function(data,status){
           if(data.flash){
                $('#flash').text(data.flash.msg).show();
                $('#vercode').attr('style','border-color:#800000;');
                get_vercode();

           }else{
               var _id = data._id;
               $("#code-id").attr("value", _id);
               var count = 90;
                var countdown = setInterval(CountDown, 1000);
                function CountDown() {
                    $("#send-email").attr("disabled", true);
                    $("#send-email").val(count + "s 后重发");
                    if (count == 0) {
                        $("#send-email").val("重新发送").removeAttr("disabled");
                        clearInterval(countdown);
                    }
                    count--;
                }


           }

      });
    }

}

// 改变消息状态
function msg_status(id){
        var cnt = parseInt($('#top-msg-cnt').text())-1;
        $.post("/api/msg/status",{id:id});
//        $('#top-msg-cnt').text(cnt);
//        $('#menu-msg-cnt').text(cnt);
//        $('#menu-msg-cnt').text(cnt);
//        $('#not-msg-cnt').text(cnt);
//        $('#'+id).remove();
}

// 改变消息状态
function msg_status_all(){
        var cnt = 0;
        $.post("/api/msg/status/all",function(data,status){
            $('#top-msg-cnt').text(cnt);
            $('#menu-msg-cnt').text(cnt);
            $('#menu-msg-cnt').text(cnt);
            $('#not-msg-cnt').text(cnt);
        });

}

// 改变消息状态
function msg_status_p(id){
        var cnt = parseInt($('#top-msg-cnt').text())-1;
        $.post("/api/msg/status",{id:id});
        $('#top-msg-cnt').text(cnt);
        $('#menu-msg-cnt').text(cnt);
        $('#menu-msg-cnt').text(cnt);
        $('#not-msg-cnt').text(cnt);
        $('#'+id).remove();
}

// delete消息
function msg_status_del(id){
        $.post("/api/msg/delete",{id:id});
        $('#'+id).remove();
}

//为浏览器的生id
function uuid() {
    var s = [];
    var hexDigits = "0123456789abcdef";
    for (var i = 0; i < 36; i++) {
        s[i] = hexDigits.substr(Math.floor(Math.random() * 0x10), 1);
    }
    s[14] = "4";  // bits 12-15 of the time_hi_and_version field to 0010
    s[19] = hexDigits.substr((s[19] & 0x3) | 0x8, 1);  // bits 6-7 of the clock_seq_hi_and_reserved to 01
    s[8] = s[13] = s[18] = s[23] = "-";

    var uuid = s.join("");
    return uuid;
}

function add_pageview(){
    url = window.location.href;
    $.post("/api/pageview/add",{url:url});
}

function getCookie(c_name)
{
    if (document.cookie.length>0)
      {
      c_start=document.cookie.indexOf(c_name + "=")
      if (c_start!=-1)
        {
        c_start=c_start + c_name.length+1
        c_end=document.cookie.indexOf(";",c_start)
        if (c_end==-1) c_end=document.cookie.length
        return unescape(document.cookie.substring(c_start,c_end))
        }
      }
    return ""
}

function setCookie(c_name,value,expiredays)
{
    var exdate=new Date()
    exdate.setDate(exdate.getDate()+expiredays)
    document.cookie=c_name+ "=" +escape(value)+
    ((expiredays==null) ? "" : ";expires="+exdate.toGMTString())
}

//function checkCookie()
//{
//    var pid = $('#post-id').text();
//    if(pid){
//        var pv_cnt = parseInt($("#pv").text());
//        noobw_id=getCookie('noobw_post'+pid)
//        if (noobw_id!=null && noobw_id!="")
//        {
//            $.post("/api/post/add-pv",{id:pid,ua_id:noobw_id},function(data,status){
//                if(data.add){
//                    $('#pv').text(pv_cnt+1)
//                }
//            });
//        }
//        else
//          {
//            var noobw_id = uuid();
//            setCookie('noobw_post'+pid, noobw_id, 365)
//            $.post("/api/post/add-pv",{id:pid,ua_id:noobw_id},function(data,status){
//                if(data.add){
//                    $('#pv').text(pv_cnt+1)
//                }
//
//            });
//          }
//    }
//}

//返回顶部
function b() {
	h = $(window).height(),
	t = $(document).scrollTop(),
	t > h ? $("#moquu_top").show() : $("#moquu_top").hide()
}
function to_top() {
	b(),
	$(document).scrollTop(0)
}

$(window).scroll(function() {
	b()
});



