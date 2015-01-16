class PeChat
    received_last: 1
    site_id: false

    clear_message: (placeholder="") ->
        $("#PeChatMessageArea").val("")
        $("#PeChatMessageArea").attr("placeholder", placeholder)

    set_nickname: ->
        this.interval = setInterval("PeChat.prototype.reload()", 5000)
        this.nickname = $("#PeChatMessageArea").val()
        PeChat.prototype.clear_message( "メッセージ")

    append_log: (comments, received_last) ->
        for comment in comments
            $("#PeChatLogTextArea").prepend("#{comment['nickname']} -> #{comment['message']}\n")
            PeChat.prototype.received_last = received_last

    reload: ->
        $.ajax(
            type: "GET"
            url: "http://pechat.w32.jp/comment/#{PeChat.prototype.site_id}/receive/"
            data: {
                received_last: PeChat.prototype.received_last
                }
            dataType: "jsonp"
            jsonpCallback: "pechat"
            success: (json) =>
                PeChat.prototype.append_log(json["comments"], json["received_last"])
        )

    send: ->
        message = $("#PeChatMessageArea").val()
        if message.length <= 1
            return false

        $.ajax(
            type: "GET"
            url: "http://pechat.w32.jp/comment/#{PeChat.prototype.site_id}/"
            data: {
                nickname: this.nickname
                message: message
                received_last: PeChat.prototype.received_last
                }
            dataType: "jsonp"
            jsonpCallback: "pechat"
            success: (json) =>
                PeChat.prototype.append_log(json["comments"], json["received_last"])
        )
        PeChat.prototype.clear_message()

    constructor: (site_id) ->
        console.log("PeChat starting...")
        PeChat.prototype.site_id = site_id
        $("body").append("""
            <div id="PeChat">
      <div id="PeChatStatus" onclick="$('#PeChatWindow').toggle()">
        <img src="http://pechat.w32.jp/static/image/icon.png">
      </div>
      <div id="PeChatWindow">
	<div id="PeChatLog">
	  <textarea id="PeChatLogTextArea" disabled="disabled"></textarea>
	</div>
	<div id="PeChatControl">
	  <input type="text" id="PeChatMessageArea" placeholder="">
	  <button name="set" id="PeChatNicknameSet">Send</button>
	  <button name="send" id="PeChatMessageSend" >Send</button>
	</div>
      </div>
    </div>
        """)
        $("#PeChatNicknameSet").click( ->
            PeChat.prototype.set_nickname()
            $("#PeChatNicknameSet").hide()
            $("#PeChatMessageSend").show()
        )
        $("#PeChatMessageSend").click( ->
            PeChat.prototype.send()
        )
        PeChat.prototype.clear_message("ニックネーム")
