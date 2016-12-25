
function a_time_str(){
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

}
// delete post
function user_post_del(id){
   confirm_alert();
   Modal.confirm({msg: "确定删除？"})
   .on( function (e) {
        if(e){
            $.post("/api/post/delete",{pid:id});
            $('#'+id).remove();
            $('#op'+id).remove();
            }
    });
}

// 查询post
  function get_post(_sub){
    $('#post-list').empty() ;
    $("#more").text("加载中...");
    $.get("/api/posts",{sub:_sub},function(data,status){
        var posts = data.posts;
        $("#n_page").attr("href", data.n_page)
       if (data.n_page == "0"){
            $("#more").text("已经到底了");
            $("#more").attr('style', "color:#808080;");
        }else{
            $("#more").text("点击查看更多");
            $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
        }
        $('#PostTemp').tmpl(posts).appendTo('#post-list');
        a_time_str();
   });
  }

  //查看更多post
  function post_more(){
    var _sub = $("a.get-posts").attr("id");
    var n_page = $("#n_page").attr("href");
    if (n_page == "0"){
        $("#more").text("已经到底了");
        $("#more").attr('style', "color:#808080;");
    }else{
        $("#more").text("加载中...");
        $.get("/api/posts",{sub:_sub, page:n_page},function(data,status){
            var posts = data.posts;
            $("#n_page").attr("href", data.n_page);
            if (data.n_page == "0"){
                $("#more").text("已经到底了");
                $("#more").attr('style', "color:#808080;");
            }else{
                $("#more").text("点击查看更多");
                $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
            }
            $('#PostTemp').tmpl(posts).appendTo('#post-list');
            a_time_str();

        });
     }

  }

// 查询用户post
function get_user_post(_sub, _uid){

    $("#more").attr('onclick', "user_post_more("+_uid+")");
    $("#s_flash").text("");
    $('#post-list').empty() ;
    $("#more").text("加载中...");
    $.get("/api/posts",{sub:_sub, user_id: _uid},function(data,status){
        var posts = data.posts
        $("#n_page").attr("href", data.n_page)
       if (data.n_page == "0"){
            $("#more").text("已经到底了");
            $("#more").attr('style', "color:#808080;");
        }else{
            $("#more").text("点击查看更多");
            $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
        }
        $('#PostTemp').tmpl(posts).appendTo('#post-list');
        a_time_str();
   });
  }



  //查看更多用户post
  function user_post_more(_uid){
    var _sub = $("a.get-posts").attr("id");
    var n_page = $("#n_page").attr("href");
    if (n_page == "0"){
        $("#more").text("已经到底了");
        $("#more").attr('style', "color:#808080;");
    }else{
        $("#more").text("加载中...");
        $.get("/api/posts",{sub:_sub, page:n_page,user_id: _uid},function(data,status){
            var posts = data.posts;
            $("#n_page").attr("href", data.n_page);
            if (data.n_page == "0"){
                $("#more").text("已经到底了");
                $("#more").attr('style', "color:#808080;");
            }else{
                $("#more").text("点击查看更多");
                $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
            }
            $('#PostTemp').tmpl(posts).appendTo('#post-list');
            a_time_str();

        });
     }

  }

//查看更多此类型post
  function post_type_more(){
    var _sub = $("p.get-posts").attr("id");
    var type = $("p.post-type").attr("id");
    var n_page = $("#n_page").attr("href");
    if (n_page == "0"){
        $("#more").text("已经到底了");
        $("#more").attr('style', "color:#808080;");
    }else{
        if (type == "type"){
            var filter = {type:_sub, page:n_page};

        }else{
            var filter = {tag:_sub, page:n_page};
        }
        $("#more").text("加载中...");
        $.get("/api/posts/type",filter,function(data,status){
            var posts = data.posts;
            $("#n_page").attr("href", data.n_page);
            $('#PostTemp').tmpl(posts).appendTo('#post-list');
            if (data.n_page == "0"){
                $("#more").text("已经到底了");
                $("#more").attr('style', "color:#808080;");
            }else{
                $("#more").text("点击查看更多");
                $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
            }
            a_time_str();

        });
     }
  }


//查看更多此专题post
  function post_sub_more(){
    var _sub = $("p.get-posts").attr("id");
    var n_page = $("#n_page").attr("href");
    if (n_page == "0"){
        $("#more").text("已经到底了");
        $("#more").attr('style', "color:#808080;");
    }else{
        var filter = {'subject':_sub, 'page':n_page}
        $("#more").text("加载中...");
        $.get("/api/posts/subject",filter,function(data,status){
            var posts = data.posts;
            $("#n_page").attr("href", data.n_page);
            $('#PostTemp').tmpl(posts).appendTo('#post-list');
            if (data.n_page == "0"){
                $("#more").text("已经到底了");
                $("#more").attr('style', "color:#808080;");
            }else{
                $("#more").text("点击查看更多");
                $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
            }
            a_time_str();

        });
     }
  }


//comment delete
function del_comment(cid){
    $.post("/api/comment/delete",{cid:cid},function(data,status){
        $("#"+cid).remove();
        $("#comment-top").text( parseInt($("#comment-top").text()) - 1+"条评论" )
        $("#comment-cnt").text( parseInt($("#comment-cnt").text()) - 1)
    });

  }

//comment more
  function comment_more(post_id){
    var n_page = $("#n_page").attr("href");
    if (n_page == "0"){
        $("#more").text("没有评论了");
        $("#more").attr('style', "color:#808080;");
    }else{
        $("#more").text("加载中...");
        $.get("/api/comments",{post_id:post_id, page:n_page},function(data,status){
            var comments = data.comments;
            $("#n_page").attr("href", data.n_page);
            $('#CommentTemp').tmpl(comments).appendTo('#comment-list')
            if (data.n_page == "0"){
                $("#more").text("没有评论了");
                $("#more").attr('style', "color:#808080;");
            }else{
                $("#more").text("查看更多评论");
                $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
            }
            a_time_str();

        });
     }
  }

 //comment add
function add_comment(post_id, reply_id){
    $('#flash').empty();
    var username = $("#username").val();
    var email = $("#email").val();
//    if (!username){
//        $('#flash').text("游客必须填写名号!");
//    }else if(!email){
//        $('#flash').text("游客必须填写邮箱,邮箱不会公布！");
//    }
//    else if(/^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(email) == false){
//        $('#flash').text("邮箱格式不对哦!");
//    }else{
        // 记录游客名号和邮箱到浏览器的
        setCookie('visitor_email', email, 365)
        setCookie('visitor_name', username, 365)
        // ---------------------------------
        if(reply_id){
            var comment = $("#comment"+reply_id).val();
        }else{
             var comment = $("#comment").val();
        }
        $("#more").text("查看更多评论");
        $.post("/api/comment/add",
        {username:username, email:email, case_id:post_id, reply_id:reply_id, comment:comment},
        function(data,status){
            if (data.flash){
                if(reply_id){
                    if(data.flash.type == "html"){
                        $('#flash-'+reply_id).append(data.flash.msg);
                    }else{
                        $('#flash-'+reply_id).text(data.flash.msg);
                    }

                }else{
                    if(data.flash.type == "html"){
                        $('#flash').append(data.flash.msg);
                    }else{
                        $('#flash').text(data.flash.msg);
                    }
                }

            }else{
                $("#comment").val("");
                $("#comment-top").text( parseInt($("#comment-top").text()) + 1+"条评论" )
                $("#comment-cnt").text( parseInt($("#comment-cnt").text()) + 1)
                if (data.anonymous){
                     $("#wait-review").text('  评论等待审核...')
                }
                $.get("/api/comments",{post_id:post_id, page:1},function(data,status){
                    var comments = data.comments;
                    $("#n_page").attr("href", data.n_page);
                    $('#comment-list').empty()
                    $('#CommentTemp').tmpl(comments).appendTo('#comment-list')
                    if (data.n_page == "0"){
                        $("#more").text("没有评论了");
                        $("#more").attr('style', "color:#808080;");
                    }else{
                        $("#more").text("查看更多评论");
                        $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
                    }
                    a_time_str();
                    });
            }

        });
    //}
 }
//回复按钮

function reply_btn(post_id,cid){

    var _onlick = "add_comment('" + post_id + "','"  + cid + "')";
    var html = '<div class="form-group">'
                //+'<script type="text/plain" id="comment"'+ cid +'"  style="width:100%;height:120px;"></script>'
             +'<textarea id="comment'+ cid +'" class="form-control" id="comment" name="comment" placeholder="回复点什么?" rows="5"></textarea>'
              +'<a id="flash-'+cid+'" style="color:#800000;"></a>'
              +'</div>'
              +'<div class="form-group">'
              +'<a class="btn btn-dark" onclick="' + _onlick + '" >＋回复</a>'
              +'</div>';
    $("#reply"+cid).empty();
    $("#reply"+cid).append(html);
}

 //赞+
function praise_a(post_id){
    var _cnt = parseInt($("#praise-cnt").text());
    $.post("/api/praise/add",{post_id:post_id},function(data,status){
        $("#praise").attr('class', "fa fa-heart")
        $("#praise-cnt").text(_cnt+1)
        var _id = $("#post-id").text()
        $("#praise").attr('onclick', "praise_s('" + _id + "')")

    });
 }
  //赞-
function praise_s(post_id){
    var _cnt = parseInt($("#praise-cnt").text());
    $.post("/api/praise/sub",{post_id:post_id},function(data,status){
        $("#praise").attr('class', "icon-heart")
        $("#praise-cnt").text(_cnt-1)
        var _id = $("#post-id").text()
        $("#praise").attr('onclick', "praise_a('" + _id + "')")
    });
 }

//msg
// 查询用户msg
  function get_user_msg(_sta, _uid){
    $('#msg-list').empty() ;
    $("#more").text("加载中...");
    $.get("/api/msgs",{sta:_sta, user_id: _uid},function(data,status){
        var msgs = data.msgs
        $("#n_page").attr("href", data.n_page)
       if (data.n_page == "0" || data.n_page == 0){
            $("#more").text("已经到底了");
            $("#more").attr('style', "color:#808080;");
        }else{
            $("#more").text("点击查看更多");
            $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
        }
        $('#MsgTemp').tmpl(msgs).appendTo('#msg-list');
        a_time_str();
   });
  }

//查看更多用户msg
function user_msg_more(_uid){
var _sta = $("a.get-msgs").attr("id");
var n_page = $("#n_page").attr("href");
if (n_page == "0"){
    $("#more").text("已经到底了");
    $("#more").attr('style', "color:#808080;");
}else{
    $("#more").text("加载中...");
    $.get("/api/msgs",{sta:_sta, page:n_page,user_id: _uid},function(data,status){
        var msgs = data.msgs;
        $("#n_page").attr("href", data.n_page);
        if (data.n_page == "0"){
            $("#more").text("已经到底了");
            $("#more").attr('style', "color:#808080;");
        }else{
            $("#more").text("点击查看更多");
            $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
        }
        $('#MsgTemp').tmpl(msgs).appendTo('#msg-list');
        a_time_str();

    });
 }

}


//用户文章搜索
 function s_posts(user_id){

    $('#post-list').empty() ;
    $('#post-l-nav a').removeClass("btn-success get-posts");
    //----------------------
    var n_page = 1;
    var s = $("#s_post").val();
    if(!s){
        $("#s_flash").text("请输入关键字");
    }else{
        $("#s_flash").text("正在搜索...");
        $.get("/api/s/posts",{s:s, user_id:user_id, page:n_page},function(data,status){
            var posts = data.posts
            $("#n_page").attr("href", data.n_page)
               if (data.n_page == "0"){
                    $("#more").text("已经到底了");
                    $("#more").attr('style', "color:#808080;");
                }else{
                    $("#more").text("点击查看更多");
                    $("#more").attr('style', "border-color:#1ab667;color:#1AB667;");
                    $("#more").attr('onclick', "s_posts_more(" + user_id + ",'" + s + "')");
                }

                if(data.post_cnt==0){
                    $("#s_flash").text("未找到相关文章!");
                }else{
                    $('#PostTemp').tmpl(posts).appendTo('#post-list');
                    a_time_str();
                    $("#s_flash").text("搜索结果")
                }
                a_time_str();
           });
    }
  }

//用户文章搜索more
 function s_posts_more(user_id, s){

    $('#post-l-nav a').removeClass("btn-success get-posts");
    //----------------------
    var n_page = $("#n_page").attr("href");
    if(!s){
        var s = $("#s_post").val();
    }
    if(!s){
        $("#s_flash").text("请输入关键字");
    }else{
        $("#s_flash").text("正在搜索...");
        $.get("/api/s/posts",{s:s, user_id:user_id, page:n_page},function(data,status){
            var posts = data.posts
            $("#n_page").attr("href", data.n_page)
           if (data.n_page == "0"){
                $("#more").text("已经到底了");
                $("#more").attr('style', "color:#808080;");
            }
            if(data.post_cnt!=0){
                $('#PostTemp').tmpl(posts).appendTo('#post-list');
                a_time_str();
                $("#s_flash").text("搜索结果")
            }
            a_time_str();
        });
    }
  }

  //全部文章搜索
 function s_all_posts(page){
    $('#post-list').empty();
    var now_page =  $("#page").val();
    //----------------------
    if(page=="next"){
        var n_page = parseInt(now_page)+1
    }else if(page=="last"){
        var n_page = parseInt(now_page)-1
    }else{
        var n_page = parseInt(page)
    }
    var s = $("#s-key-word").val();
    //修改URL
    var r = changeURLPar(window.location.href, "page",n_page)
        var state = {};
         window.history.pushState(state, null, r);
    //
    if (n_page<=0){
        $("#s_flash").text("404 没有相关页面!");
    }else{
        //------------------------------------
        $("#s_flash").text("正在搜索...");
        $.get("/api/s/posts",{s:s,page:n_page},function(data,status){
            var posts = data.posts
            if(data.post_cnt==0){
                window.location.href = "/search?page="+n_page+"&s="+s;
            }else{
                $("#s_flash").text("");
                $('#PostTemp').tmpl(posts).appendTo('#post-list');
                a_time_str();
                $("#page").val(n_page);
                if(data.flash){
                    $("#s_flash").text(data.flash.msg);
                }
                //nav 高亮
                $("#"+n_page).addClass("active").siblings().removeClass("active");
                if(n_page==1){
                    $("#last_page_li").hide();
                }else if(n_page>1){
                    $("#last_page_li").show();
                }
                if(n_page==data.page_cnt){
                    $("#next_page_li").hide();
                }else{
                    $("#next_page_li").show();
                }
            }
            a_time_str();
        });
    }

  }

//更改地址栏搜索
function changeURLPar(destiny, par, par_value){
    var pattern = par+'=([^&]*)';
    var replaceText = par+'='+par_value;
    if (destiny.match(pattern)){
        var tmp = '/\\'+par+'=[^&]*/';
        tmp = destiny.replace(eval(tmp), replaceText);
        return (tmp);
    } else {
        if (destiny.match('[\?]')){
            return destiny+'&'+ replaceText;
        }else {
            return destiny+'?'+replaceText;
        }
    }
    return destiny+'\n'+par+'\n'+par_value;
}

function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]); return null; //返回参数值
}

