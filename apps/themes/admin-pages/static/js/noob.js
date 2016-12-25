//post导航高亮
$(function(){
        $('#post-l-nav a').eq(0).addClass("btn-success get-posts");
        $('#post-l-nav a').each(function(){
            $(this).click(function(){
                $(this).addClass("btn-success get-posts").siblings().removeClass("btn-success get-posts");
            })
        })
})

//user-msg导航高亮
$(function(){
        $('#u-msg-l-nav a').eq(0).addClass("btn-success get-posts");
        $('#u-msg-l-nav a').each(function(){
            $(this).click(function(){
                 $(this).addClass("btn-success get-msgs").siblings().removeClass("btn-success get-msgs");
            })
        })
})

//导航高亮
$(document).ready(function(){
var sub={s:'b'}
    //jQuery methods go here...
    $('#'+sub.s).addClass("act")

});



