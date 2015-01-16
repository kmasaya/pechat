// Generated by CoffeeScript 1.4.0
var PeChat;

PeChat = (function() {

  PeChat.prototype.received_last = 1;

  PeChat.prototype.site_id = false;

  PeChat.prototype.clear_message = function(placeholder) {
    if (placeholder == null) {
      placeholder = "";
    }
    $("#PeChatMessageArea").val("");
    return $("#PeChatMessageArea").attr("placeholder", placeholder);
  };

  PeChat.prototype.set_nickname = function() {
    this.interval = setInterval("PeChat.prototype.reload()", 5000);
    this.nickname = $("#PeChatMessageArea").val();
    return PeChat.prototype.clear_message("メッセージ");
  };

  PeChat.prototype.append_log = function(comments, received_last) {
    var comment, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = comments.length; _i < _len; _i++) {
      comment = comments[_i];
      $("#PeChatLogTextArea").prepend("" + comment['nickname'] + " -> " + comment['message'] + "\n");
      _results.push(PeChat.prototype.received_last = received_last);
    }
    return _results;
  };

  PeChat.prototype.reload = function() {
    var _this = this;
    return $.ajax({
      type: "GET",
      url: "http://pechat.w32.jp/comment/" + PeChat.prototype.site_id + "/receive/",
      data: {
        received_last: PeChat.prototype.received_last
      },
      dataType: "jsonp",
      jsonpCallback: "pechat",
      success: function(json) {
        return PeChat.prototype.append_log(json["comments"], json["received_last"]);
      }
    });
  };

  PeChat.prototype.send = function() {
    var message,
      _this = this;
    message = $("#PeChatMessageArea").val();
    if (message.length <= 1) {
      return false;
    }
    $.ajax({
      type: "GET",
      url: "http://pechat.w32.jp/comment/" + PeChat.prototype.site_id + "/",
      data: {
        nickname: this.nickname,
        message: message,
        received_last: PeChat.prototype.received_last
      },
      dataType: "jsonp",
      jsonpCallback: "pechat",
      success: function(json) {
        return PeChat.prototype.append_log(json["comments"], json["received_last"]);
      }
    });
    return PeChat.prototype.clear_message();
  };

  function PeChat(site_id) {
    console.log("PeChat starting...");
    PeChat.prototype.site_id = site_id;
    $("body").append("            <div id=\"PeChat\">\n      <div id=\"PeChatStatus\" onclick=\"$('#PeChatWindow').toggle()\">\n        <img src=\"http://pechat.w32.jp/static/image/icon.png\">\n      </div>\n      <div id=\"PeChatWindow\">\n<div id=\"PeChatLog\">\n  <textarea id=\"PeChatLogTextArea\" disabled=\"disabled\"></textarea>\n</div>\n<div id=\"PeChatControl\">\n  <input type=\"text\" id=\"PeChatMessageArea\" placeholder=\"\">\n  <button name=\"set\" id=\"PeChatNicknameSet\">Send</button>\n  <button name=\"send\" id=\"PeChatMessageSend\" >Send</button>\n</div>\n      </div>\n    </div>");
    $("#PeChatNicknameSet").click(function() {
      PeChat.prototype.set_nickname();
      $("#PeChatNicknameSet").hide();
      return $("#PeChatMessageSend").show();
    });
    $("#PeChatMessageSend").click(function() {
      return PeChat.prototype.send();
    });
    PeChat.prototype.clear_message("ニックネーム");
  }

  return PeChat;

})();
