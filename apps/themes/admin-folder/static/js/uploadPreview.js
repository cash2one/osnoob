/*
*界面构造(IMG标签外必须拥有DIV 而且必须给予DIV控件ID)
* <div id="imgdiv"><img id="imgShow" width="120" height="120" /></div>
* <input type="file" id="up_img" />
*调用代码:
* new uploadPreview({ UpBtn: "up_img", DivShow: "imgdiv", ImgShow: "imgShow" });
*参数说明:
*UpBtn:选择文件控件ID;
*DivShow:DIV控件ID;
*ImgShow:图片控件ID;
*Width:预览宽度;
*Height:预览高度;
*ImgType:支持文件类型 格式:["jpg","png"];
*callback:选择文件后回调方法;
*ImgInfo:显示图片消息
*MaxImg:限制最大上传大小

*版本:v1.4
更新内容如下:
1.修复回调.

*版本:v1.3
更新内容如下:
1.修复多层级框架获取路径BUG.
2.去除对jquery插件的依赖.
*/

/*
*author:周祥
*date:2014年12月12日
*work:图片预览插件
*/




var uploadPreview = function(setting) {


    /*
	以下作者：周详
    *date:2014年12月11日
    *work:this(当前对象)
    */
    var _self = this;
    /*
    *date:2014年12月11日
    *work:判断为null或者空值
    */

    _self.IsNull = function(value) {
        if (typeof (value) == "function") { return false; }
        if (value == undefined || value == null || value == "" || value.length == 0) {
            return true;
        }
        return false;
    }
    /*
    *date:2014年12月11日
    *work:默认配置
    */
    _self.DefautlSetting = {
        UpBtn: "",
        DivShow: "",
        ImgShow: "",
        Width: 100,
        Height: 100,
        ImgType: ["gif", "jpeg", "jpg", "bmp", "png", "ico"],
        ErrMsg: "图片类型必须是(gif,jpeg,jpg,bmp,png)中的一种",
        callback: function() { }
    };
    /*
    *date:2014年12月11日
    *work:读取配置
    */
    _self.Setting = {
        UpBtn: _self.IsNull(setting.UpBtn) ? _self.DefautlSetting.UpBtn : setting.UpBtn,
        DivShow: _self.IsNull(setting.DivShow) ? _self.DefautlSetting.DivShow : setting.DivShow,
        ImgShow: _self.IsNull(setting.ImgShow) ? _self.DefautlSetting.ImgShow : setting.ImgShow,
        IsAva:  _self.IsNull(setting.ImgShow) ? _self.DefautlSetting.ImgShow : setting.IsAva,
        Width: _self.IsNull(setting.Width) ? _self.DefautlSetting.Width : setting.Width,
        Height: _self.IsNull(setting.Height) ? _self.DefautlSetting.Height : setting.Height,
        ImgType: _self.IsNull(setting.ImgType) ? _self.DefautlSetting.ImgType : setting.ImgType,
        ErrMsg: _self.IsNull(setting.ErrMsg) ? _self.DefautlSetting.ErrMsg : setting.ErrMsg,
        callback: _self.IsNull(setting.callback) ? _self.DefautlSetting.callback : setting.callback,
        MaxSize: _self.IsNull(setting.MaxSize) ? _self.DefautlSetting.MaxSize : setting.MaxSize,
        ImgInfo: _self.IsNull(setting.ImgInfo) ? _self.DefautlSetting.ImgInfo : setting.ImgInfo
    };
    /*
    *date:2014年12月11日
    *work:获取文本控件URL
    */
    _self.getObjectURL = function(file) {
        var url = null;
        if (window.createObjectURL != undefined) {
            url = window.createObjectURL(file);
        } else if (window.URL != undefined) {
            url = window.URL.createObjectURL(file);
        } else if (window.webkitURL != undefined) {
            url = window.webkitURL.createObjectURL(file);
        }
        return url;
    }

	 /*
    *author:Allen Woo
    *date:2016年3月30日
    */
	var fileChange = function(target){
		//检测上传文件的类型
		var imgName = document.getElementById(_self.Setting.UpBtn).value;
		 var ext,idx;

		//检测上传文件的大小
		var isIE = /msie/i.test(navigator.userAgent) && !window.opera;
		var fileSize = 0;
		if (isIE && !target.files){
			var filePath = target.value;
			var fileSystem = new ActiveXObject("Scripting.FileSystemObject");
			var file = fileSystem.GetFile (filePath);
			fileSize = file.Size;
		} else {
			fileSize = target.files[0].size;
		}
		var size = fileSize / 1024*1024;
		if(size>(1024*_self.Setting.MaxSize)){
		    document.all.submit.disabled=true;
		    var _msg = "<span style='color:#BC1828;'>图片大于了"+_self.Setting.MaxSize+"Kb</span>";
		    document.getElementById(_self.Setting.ImgInfo).innerHTML = _msg;
		}else{
		    var _msg = "点击修改";
		    document.getElementById(_self.Setting.ImgInfo).innerHTML = _msg;
		    document.all.submit.disabled=false;
		}

	}

    /*
    *date:2014年12月11日
    *work:绑定事件
    */
    _self.Bind = function() {
        document.getElementById(_self.Setting.UpBtn).onchange = function() {
			fileChange(this);
            if (this.value) {
                if (!RegExp("\.(" + _self.Setting.ImgType.join("|") + ")$", "i").test(this.value.toLowerCase())) {
					var _msg = "<span style='color:#BC1828;'>"+_self.Setting.ErrMsg+"</span>"
					document.getElementById(_self.Setting.ImgInfo).innerHTML = _msg
                    this.value = "";
                    return false;
                }
                if (navigator.userAgent.indexOf("MSIE") > -1) {
                    try {
                        document.getElementById(_self.Setting.ImgShow).src = _self.getObjectURL(this.files[0]);
                        if(_self.Setting.IsAva){
                            document.getElementById('pic1').src = _self.getObjectURL(this.files[0]);
                            document.getElementById('pic2').src = _self.getObjectURL(this.files[0]);

                        }
                    } catch (e) {
                        var div = document.getElementById(_self.Setting.DivShow);
                        this.select();
                        top.parent.document.body.focus();
                        var src = document.selection.createRange().text;
                        document.selection.empty();
                        document.getElementById(_self.Setting.ImgShow).style.display = "none";
                        div.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale)";
                        div.style.width = _self.Setting.Width + "px";
                        div.style.height = _self.Setting.Height + "px";
                        div.filters.item("DXImageTransform.Microsoft.AlphaImageLoader").src = src;
                    }
                } else {
                    document.getElementById(_self.Setting.ImgShow).src = _self.getObjectURL(this.files[0]);
                    if(_self.Setting.IsAva){
                            document.getElementById('pic1').src = _self.getObjectURL(this.files[0]);
                            document.getElementById('pic2').src = _self.getObjectURL(this.files[0]);

                    }
                }
                _self.Setting.callback();
            }
        }
    }
    /*
    *date:2014年12月11日
    *work:执行绑定事件
    */
    _self.Bind();
}