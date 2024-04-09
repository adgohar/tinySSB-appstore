// tremola.js

"use strict";

var tremola;
var curr_chat;
var qr;
var myId;
var localPeers = {}; // feedID ~ [isOnline, isConnected] - TF, TT, FT - FF means to remove this entry
var must_redraw = false;
var edit_target = '';
var new_contact_id = '';
var colors = ["#d9ceb2", "#99b2b7", "#e6cba5", "#ede3b4", "#8b9e9b", "#bd7578", "#edc951",
    "#ffd573", "#c2a34f", "#fbb829", "#ffab03", "#7ab317", "#a0c55f", "#8ca315",
    "#5191c1", "#6493a7", "#bddb88"]
var curr_img_candidate = null;
var pubs = []
var wants = {}

var restream = false // whether the backend is currently restreaming all posts

// --- menu callbacks

/*
function menu_sync() {
  if (localPeers.length == 0)
    launch_snackbar("no local peer to sync with");
  else {
    for (var i in localPeers) {
      backend("sync " + i);
      launch_snackbar("sync launched");
      break
    }
  }
  closeOverlay();
}
*/

function appController() {
    document.getElementById("appScreen").style.display = "none";
    //addAppFile("RDR2", "main.js", "ZnVuY3Rpb24gYXBwQWN0aW9uKCkgew0KICAgIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCJhcHBEaXYiKS5pbm5lckhUTUwgPSAiUHJvdGFnb25pc3QgaXMgU2FkaWUgQWRsZXIhIjsNCn0");
    //addAppFile("RDR2", "main.html", "PCFET0NUWVBFIGh0bWw+DQo8aHRtbCBsYW5nPSJlbiI+DQoNCjxoZWFkPg0KICA8bWV0YSBjaGFyc2V0PSJVVEYtOCIgLz4NCiAgPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiIC8+DQo8L2hlYWQ+DQoNCjxib2R5Pg0KICAgIDxoMT4NCiAgICAgICAgVGhlIGN1cnJlbnQgSFRNTCBGaWxlIGlzIHdyb25nLg0KICAgIDwvaDE+DQogICAgPGRpdiBzdHlsZT0iYWxpZ24taXRlbXM6IGNlbnRlciI+DQogICAgICAgIDxkaXYgaWQ9ImFwcERpdiIgc3R5bGU9ImZvbnQtd2VpZ2h0OiBib2xkOyI+T3JpZ2luYWwgVGV4dDwvZGl2Pg0KICAgICAgICA8YnV0dG9uIGNsYXNzPSIiIHN0eWxlPSIiIG9uY2xpY2s9ImFwcEFjdGlvbigpIj5PbGQgQnV0dG9uPC9idXR0b24+DQogICAgPC9kaXY+DQo8L2JvZHk+DQoNCjwvaHRtbD4=");
    addAppFile("RDR2", "main.js", "ZnVuY3Rpb24gYXBwQWN0aW9uKCkgew0KICAgIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCJhcHBEaXYiKS5pbm5lckhUTUwgPSAiUHJvdGFnb25pc3QgaXMgQXJ0aHVyIE1vcmdhbiEiOw0KfQ==");
    addAppFile("RDR2", "main.html", "PCFET0NUWVBFIGh0bWw+DQo8aHRtbCBsYW5nPSJlbiI+DQoNCjxoZWFkPg0KICA8bWV0YSBjaGFyc2V0PSJVVEYtOCIgLz4NCiAgPG1ldGEgbmFtZT0idmlld3BvcnQiIGNvbnRlbnQ9IndpZHRoPWRldmljZS13aWR0aCwgaW5pdGlhbC1zY2FsZT0xLjAiIC8+DQo8L2hlYWQ+DQoNCjxib2R5Pg0KICAgIDxoMT4NCiAgICAgICAgUmVkIERlYWQgUmVkZW1wdGlvbiBJSQ0KICAgIDwvaDE+DQogICAgPGRpdiBzdHlsZT0iYWxpZ24taXRlbXM6IGNlbnRlciI+DQogICAgICA8YnV0dG9uIGNsYXNzPSIiIHN0eWxlPSIiIG9uY2xpY2s9ImFwcEFjdGlvbigpIj5BcHAgUHJvbXB0PC9idXR0b24+DQogICAgICA8ZGl2IGlkPSJhcHBEaXYiIHN0eWxlPSJmb250LXdlaWdodDogYm9sZDsiPk9yaWdpbmFsIFRleHQ8L2Rpdj4NCiAgICA8L2Rpdj4NCjwvYm9keT4NCg0KPC9odG1sPg==" );

    addApp("Witcher-III", "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");
    //removeApp("Witcher-III")
    getApps();
}

function displayAppCreationUI() {
    document.getElementById("appCreationModal").style.display = "block";
    overlayIsActive = true;
}

function getApps() {
    backend("apps:listApps");
}

function addApp(appName, appIconBase64) {
    backend("apps:addApp " + appName + " " + appIconBase64);
}

function addAppFile(appName, fileName, fileBase64) {
    backend("apps:updateApp " + appName + " " + fileName + " " + fileBase64);
}

function removeApp(appName) {
    backend("apps:removeApp " + appName);
}

function listApps(appNameListString, appIconListString) {
    const appNameList = JSON.parse(appNameListString);
    const appIconList = JSON.parse(appIconListString);
    removeAllAppsUI();
    let i = 0;
    for (const appName of appNameList) {
        createAppUI(appName, appIconList[i]);
        i += 1;
    }
}

function removeAllAppsUI() {
    const appListUI = document.getElementById('appsList');
    while (appListUI.firstChild) {
        appListUI.removeChild(appListUI.firstChild);
    }
}

function loadApp(appName) {
    backend("apps:loadApp " + appName);
}

function loadAppHTML(htmlBase64) {
    let decodedHtml = atob(htmlBase64);
    let appScreen = document.getElementById("appScreen");
    appScreen.innerHTML = decodedHtml;
}

function loadAppJS(jsBase64) {

    // Convert base64 string to a Blob
    let scriptBlob = new Blob([Uint8Array.from(atob(jsBase64), c => c.charCodeAt(0))], {type: 'application/javascript'});

    // Create a URL for the Blob
    let scriptURL = URL.createObjectURL(scriptBlob);

    // Create a new script element
    let scriptElement = document.createElement('script');

    // Set the source of the script element to the Blob URL
    scriptElement.src = scriptURL;

    // Append the script element to the document
    document.body.appendChild(scriptElement);

    // Optional: Clean up the Blob URL after the script is loaded
    scriptElement.onload = function() {
        URL.revokeObjectURL(scriptURL);
    };

    document.getElementById("appScreen").style.display = "block";
}

function createAppUI(appName, appIconBase64) {
    const appListUI = document.getElementById('appsList');

    const appButton = document.createElement('button');
    appButton.style.display = 'flex';
    appButton.style.flexDirection = 'column';
    appButton.style.alignItems = 'center';
    appButton.style.justifyContent = 'center';

    appButton.onclick = function () {
        loadApp(appName);
    };

    const imageDataUrl = `data:image/jpeg;base64,${appIconBase64}`;

    const appImage = document.createElement('img');
    appImage.src = imageDataUrl;
    appImage.alt = appName;
    appImage.style.width = '50px';
    appImage.style.height = '50px';

    const appLabel = document.createElement('span');
    appLabel.textContent = appName;

    appButton.appendChild(appImage);
    appButton.appendChild(appLabel);

    appListUI.appendChild(appButton);
}


function menu_new_conversation() {
    fill_members();
    prev_scenario = 'chats';
    setScenario("members");
    document.getElementById("div:textarea").style.display = 'none';
    document.getElementById("div:confirm-members").style.display = 'flex';
    document.getElementById("tremolaTitle").style.display = 'none';
    var c = document.getElementById("conversationTitle");
    c.style.display = null;
    c.innerHTML = "<font size=+1><strong>Create New Conversation</strong></font><br>Select up to 7 members";
    document.getElementById('plus').style.display = 'none';
    closeOverlay();
}

function menu_new_contact() {
    document.getElementById('new_contact-overlay').style.display = 'initial';
    document.getElementById('overlay-bg').style.display = 'initial';
    // document.getElementById('chat_name').focus();
    overlayIsActive = true;
}

function menu_new_pub() {
    menu_edit('new_pub_target', "Enter address of trustworthy pub<br><br>Format:<br><tt>net:IP_ADDR:PORT~shs:ID_OF_PUB</tt>", "");
}

function menu_invite() {
    menu_edit('new_invite_target', "Enter invite code<br><br>Format:<br><tt>IP_ADDR:PORT:@ID_OF_PUB.ed25519~INVITE_CODE</tt>", "");
}

function menu_redraw() {
    closeOverlay();

    load_chat_list()

    document.getElementById("lst:contacts").innerHTML = '';
    load_contact_list();

    if (curr_scenario == "posts")
        load_chat(curr_chat);
}

function menu_edit(target, title, text) {
    closeOverlay()
    document.getElementById('edit-overlay').style.display = 'initial';
    document.getElementById('overlay-bg').style.display = 'initial';
    document.getElementById('edit_title').innerHTML = title;
    document.getElementById('edit_text').value = text;
    document.getElementById('edit_text').focus();
    overlayIsActive = true;
    edit_target = target;
}

function onEnter(ev) {

    if (ev.key == "Enter") {
        switch(ev.target.id) {
            case 'edit_text':
                edit_confirmed()
                break
            case 'settings_urlInput':
                btn_setWebsocketUrl()
                break
            case 'import-id-input':
                btn_import_id()
                break
        }
    }
}

function menu_edit_convname() {
    menu_edit('convNameTarget', "Edit conversation name:<br>(only you can see this name)", tremola.chats[curr_chat].alias);
}

// function menu_edit_new_contact_alias() {
//   menu_edit('new_contact_alias', "Assign alias to new contact:", "");
// }

function edit_confirmed() {
    closeOverlay()
    console.log("edit confirmed: " + edit_target)
    var val = document.getElementById('edit_text').value;
    if (edit_target == 'convNameTarget') {
        var ch = tremola.chats[curr_chat];
        ch.alias = val;
        persist();
        load_chat_title(ch); // also have to update entry in chats
        menu_redraw();
    } else if (edit_target == 'new_contact_alias' || edit_target == 'trust_wifi_peer') {
        document.getElementById('contact_id').value = '';
        if (val == '')
            val = id2b32(new_contact_id);
        tremola.contacts[new_contact_id] = {
            "alias": val, "initial": val.substring(0, 1).toUpperCase(),
            "color": colors[Math.floor(colors.length * Math.random())],
            "iam": "", "forgotten": false
        };
        var recps = [myId, new_contact_id];
        var nm = recps2nm(recps);
        // TODO reactivate when encrypted chats are implemented
        /*
        tremola.chats[nm] = {
            "alias": "Chat w/ " + val, "posts": {}, "members": recps,
            "touched": Date.now(), "lastRead": 0, "timeline": new Timeline()
        };
        */
        persist();
        backend("add:contact " + new_contact_id + " " + btoa(val))
        menu_redraw();
    } else if (edit_target == 'new_pub_target') {
        console.log("action for new_pub_target")
    } else if (edit_target == 'new_invite_target') {
        backend("invite:redeem " + val)
    } else if (edit_target == 'new_board') {
        console.log("action for new_board")
        if (val == '') {
            console.log('empty')
            return
        }
        //create new board with name = val
        createBoard(val)
    } else if (edit_target == 'board_rename') {
        var board = tremola.board[curr_board]
        if (val == '') {
            menu_edit('board_rename', 'Enter a new name for this board', board.name)
            launch_snackbar("Enter a name")
            return
        }
        if (val == board.name) {
            menu_edit('board_rename', 'Enter a new name for this board', board.name)
            launch_snackbar('This board already have this name')
            return
        }
        renameBoard(curr_board, val)
    } else if (edit_target == 'board_new_column') {
        if (val == '') {
            menu_edit('board_new_column', 'Enter name of new List: ', '')
            launch_snackbar("Enter a name")
            return
        }
        createColumn(curr_board, val)

    } else if (edit_target == 'board_new_item') {
        if (val == '') {
            menu_edit('board_new_item', 'Enter name of new Card: ', '')
            launch_snackbar("Enter a name")
            return
        }
        createColumnItem(curr_board, curr_column, val)
    } else if (edit_target == 'board_rename_column') {
        if (val == '') {
            menu_rename_column(curr_column)
            launch_snackbar("Please enter a new Name")
            return
        }

        if (val == tremola.board[curr_board].columns[curr_column].name)
            return

        renameColumn(curr_board, curr_column, val)
    } else if (edit_target == 'board_rename_item') {

        if (val != tremola.board[curr_board].items[curr_rename_item].name && val != '') {
            renameItem(curr_board, curr_rename_item, val)
        }
        item_menu(curr_rename_item)
    }
}

function members_confirmed() {
    if (prev_scenario == 'chats') {
        new_conversation()
    } else if (prev_scenario == 'kanban') {
        menu_new_board_name()
    }
}

function menu_forget_conv() {
    // toggles the forgotten flag of a conversation
    if (curr_chat == recps2nm([myId])) {
        launch_snackbar("cannot be applied to own notes");
        return;
    }
    tremola.chats[curr_chat].forgotten = !tremola.chats[curr_chat].forgotten;
    persist();
    load_chat_list() // refresh list of conversations
    closeOverlay();
    if (curr_scenario == 'posts' /* should always be true */ && tremola.chats[curr_chat].forgotten)
        setScenario('chats');
    else
        load_chat(curr_chat) // refresh currently displayed list of posts
}

function menu_import_id() {
    closeOverlay();
    document.getElementById('import-id-overlay').style.display = 'initial'
    document.getElementById('overlay-bg').style.display = 'initial'
}

function btn_import_id() {
    var str = document.getElementById('import-id-input').value
    if(str == "")
        return
    var r = import_id(str)
    if(r) {
        launch_snackbar("Successfully imported, restarting...")
    } else {
        launch_snackbar("wrong format")
    }
}

function menu_process_msgs() {
    backend('process.msg');
    closeOverlay();
}

function menu_add_pub() {
    // ...
    closeOverlay();
}

function menu_dump() {
    backend('dump:');
    closeOverlay();
}

function menu_take_picture() {
    disabled6676863(); // breakpoint using a non-existing fct,in case
    closeOverlay();
    var draft = unicodeStringToTypedArray(document.getElementById('draft').value); // escapeHTML(
    if (draft.length == 0)
        draft = null;
    else
        draft = atob(draft);
    console.log("getVoice" + document.getElementById('draft').value);
    backend('get:voice ' + atob(draft));
}

function menu_pick_image() {
    closeOverlay();
    backend('get:media');
}

// ---

function new_text_post(s) {
    if (s.length == 0) {
        return;
    }
    var draft = unicodeStringToTypedArray(document.getElementById('draft').value); // escapeHTML(
    var recps;
    if (curr_chat == "ALL") {
        recps = "ALL";
        backend("publ:post [] " + btoa(draft) + " null"); //  + recps)
    } else {
        recps = tremola.chats[curr_chat].members.join(' ');
        backend("priv:post [] " + btoa(draft) + " null " + recps);
    }
    document.getElementById('draft').value = '';
    closeOverlay();
    setTimeout(function () { // let image rendering (fetching size) take place before we scroll
        var c = document.getElementById('core');
        c.scrollTop = c.scrollHeight;
    }, 100);
}

function new_voice_post(voice_b64) {
    var draft = unicodeStringToTypedArray(document.getElementById('draft').value); // escapeHTML(
    if (draft.length == 0)
        draft = "null"
    else
        draft = btoa(draft)
    if (curr_chat == "ALL") {
        // recps = "ALL";
        backend("publ:post [] " + draft + " " + voice_b64); //  + recps)
    } else {
        recps = tremola.chats[curr_chat].members.join(' ');
        backend("priv:post [] " + draft + " " + voice_b64 + " " + recps);
    }
    document.getElementById('draft').value = '';
}

function play_voice(nm, ref) {
    var p = tremola.chats[nm].posts[ref];
    var d = new Date(p["when"]);
    d = d.toDateString() + ' ' + d.toTimeString().substring(0, 5);
    backend("play:voice " + p["voice"] + " " + btoa(fid2display(p["from"])) + " " + btoa(d));
}

function new_image_post() {
    if (curr_img_candidate == null) {
        return;
    }
    var draft = "![](" + curr_img_candidate + ")\n";
    var caption = document.getElementById('image-caption').value;
    if (caption && caption.length > 0)
        draft += caption;
    var recps = tremola.chats[curr_chat].members.join(' ')
    backend("priv:post " + btoa(draft) + " " + recps);
    curr_img_candidate = null;
    closeOverlay();
    setTimeout(function () { // let image rendering (fetching size) take place before we scroll
        var c = document.getElementById('core');
        c.scrollTop = c.scrollHeight;
    }, 100);
}

function load_post_item(p) { // { 'key', 'from', 'when', 'body', 'to' (if group or public)>
    var pl = document.getElementById('lst:posts');
    var is_other = p["from"] != myId;
    var box = "<div class=light style='padding: 3pt; border-radius: 4px; box-shadow: 0 0 5px rgba(0,0,0,0.7); word-break: break-word;'"
    if (p.voice != null)
        box += " onclick='play_voice(\"" + curr_chat + "\", \"" + p.key + "\");'";
    box += ">"
    // console.log("box=", box);
    if (is_other)
        box += "<font size=-1><i>" + fid2display(p["from"]) + "</i></font><br>";
    var txt = ""
    if (p["body"] != null) {
        txt = escapeHTML(p["body"]).replace(/\n/g, "<br>\n");
        var re = /!\[.*?\]\((.*?)\)/g;
        txt = txt.replace(re, " &nbsp;<object type='image/jpeg' style='width: 95%; display: block; margin-left: auto; margin-right: auto; cursor: zoom-in;' data='http://appassets.androidplatform.net/blobs/$1' ondblclick='modal_img(this)'></object>&nbsp; ");
        // txt = txt + " &nbsp;<object type='image/jpeg' width=95% data='http://appassets.androidplatform.net/blobs/25d444486ffb848ed0d4f1d15d9a165934a02403b66310bf5a56757fec170cd2.jpg'></object>&nbsp; (!)";
        // console.log(txt);
    }
    if (p.voice != null)
        box += "<span style='color: red;'>&#x1f50a;</span>&nbsp;&nbsp;"
    box += txt
    var d = new Date(p["when"]);
    d = d.toDateString() + ' ' + d.toTimeString().substring(0, 5);
    box += "<div align=right style='font-size: x-small;'><i>";
    box += d + "</i></div></div>";
    var row;
    if (is_other) {
        var c = tremola.contacts[p.from]
        row = "<td style='vertical-align: top;'><button class=contact_picture style='margin-right: 0.5em; margin-left: 0.25em; background: " + c.color + "; width: 2em; height: 2em;'>" + c.initial + "</button>"
        // row  = "<td style='vertical-align: top; color: var(--red); font-weight: 900;'>&gt;"
        row += "<td colspan=2 style='padding-bottom: 10px;'>" + box + "<td colspan=2>";
    } else {
        row = "<td colspan=2><td colspan=2 style='padding-bottom: 10px;'>" + box;
        row += "<td style='vertical-align: top; color: var(--red); font-weight: 900;'>&lt;"
    }
    pl.insertRow(pl.rows.length).innerHTML = row;
}

function load_chat(nm) {
    var ch, pl, e;
    ch = tremola.chats[nm]
    if (ch.timeline == null)
        ch["timeline"] = new Timeline();
    pl = document.getElementById("lst:posts");
    while (pl.rows.length) {
        pl.deleteRow(0);
    }
    pl.insertRow(0).innerHTML = "<tr><td>&nbsp;<td>&nbsp;<td>&nbsp;<td>&nbsp;<td>&nbsp;</tr>";
    curr_chat = nm;
    var lop = []; // list of posts
    for (var p in ch.posts) lop.push(p)
    lop.sort(function (a, b) {
        return ch.posts[a].when - ch.posts[b].when
    })
    lop.forEach(function (p) {
        load_post_item(ch.posts[p])
    })
    load_chat_title(ch);
    setScenario("posts");
    document.getElementById("tremolaTitle").style.display = 'none';
    // update unread badge:
    ch["lastRead"] = Date.now();
    persist();
    document.getElementById(nm + '-badge').style.display = 'none' // is this necessary?
    setTimeout(function () { // let image rendering (fetching size) take place before we scroll
        var c = document.getElementById('core');
        c.scrollTop = c.scrollHeight;
    }, 100);
    /*
    // scroll to bottom:
    var c = document.getElementById('core');
    c.scrollTop = c.scrollHeight;
    document.getElementById('lst:posts').scrollIntoView(false)
    // console.log("did scroll down, but did it do it?")
    */
}

function load_chat_title(ch) {
    var c = document.getElementById("conversationTitle"), bg, box;
    c.style.display = null;
    c.setAttribute('classList', ch.forgotten ? 'gray' : '') // old JS (SDK 23)
    box = "<div style='white-space: nowrap;'><div style='text-overflow: ellipsis; overflow: hidden;'><font size=+1><strong>" + escapeHTML(ch.alias) + "</strong></font></div>";
    box += "<div style='color: black; text-overflow: ellipsis; overflow: hidden;'>" + escapeHTML(recps2display(ch.members)) + "</div></div>";
    c.innerHTML = box;
}

function load_chat_list() {
    var meOnly = recps2nm([myId])
    // console.log('meOnly', meOnly)
    document.getElementById('lst:chats').innerHTML = '';
    // load_chat_item(meOnly) TODO reactivate when encrypted chats are implemented
    var lop = [];
    for (var p in tremola.chats) {
        if (p != meOnly && !tremola.chats[p]['forgotten'])
            lop.push(p)
    }
    lop.sort(function (a, b) {
        return tremola.chats[b]["touched"] - tremola.chats[a]["touched"]
    })
    lop.forEach(function (p) {
        load_chat_item(p)
    })
    // forgotten chats: unsorted
    if (!tremola.settings.hide_forgotten_conv)
        for (var p in tremola.chats)
            if (p != meOnly && tremola.chats[p]['forgotten'])
                load_chat_item(p)
}

function load_chat_item(nm) { // appends a button for conversation with name nm to the conv list
    var cl, mem, item, bg, row, badge, badgeId, cnt;
    cl = document.getElementById('lst:chats');
    // console.log(nm)
    if (nm == "ALL")
        mem = "ALL";
    else
        mem = recps2display(tremola.chats[nm].members);
    item = document.createElement('div');
    // item.style = "padding: 0px 5px 10px 5px; margin: 3px 3px 6px 3px;";
    item.setAttribute('class', 'chat_item_div'); // old JS (SDK 23)
    if (tremola.chats[nm].forgotten) bg = ' gray'; else bg = ' light';
    row = "<button class='chat_item_button w100" + bg + "' onclick='load_chat(\"" + nm + "\");' style='overflow: hidden; position: relative;'>";
    row += "<div style='white-space: nowrap;'><div style='text-overflow: ellipsis; overflow: hidden;'>" + tremola.chats[nm].alias + "</div>";
    row += "<div style='text-overflow: clip; overflow: ellipsis;'><font size=-2>" + escapeHTML(mem) + "</font></div></div>";
    badgeId = nm + "-badge"
    badge = "<div id='" + badgeId + "' style='display: none; position: absolute; right: 0.5em; bottom: 0.9em; text-align: center; border-radius: 1em; height: 2em; width: 2em; background: var(--red); color: white; font-size: small; line-height:2em;'>&gt;9</div>";
    row += badge + "</button>";
    row += ""
    item.innerHTML = row;
    cl.appendChild(item);
    set_chats_badge(nm)
}

function load_contact_list() {
    document.getElementById("lst:contacts").innerHTML = '';
    for (var id in tremola.contacts)
        if (!tremola.contacts[id].forgotten)
            load_contact_item([id, tremola.contacts[id]]);
    if (!tremola.settings.hide_forgotten_contacts)
        for (var id in tremola.contacts) {
            var c = tremola.contacts[id]
            if (c.forgotten)
                load_contact_item([id, c]);
        }
}

function load_contact_item(c) { // [ id, { "alias": "thealias", "initial": "T", "color": "#123456" } ] }
    var row, item = document.createElement('div'), bg;
    item.setAttribute('style', 'padding: 0px 5px 10px 5px;'); // old JS (SDK 23)
    if (!("initial" in c[1])) {
        c[1]["initial"] = c[1].alias.substring(0, 1).toUpperCase();
        persist();
    }
    if (!("color" in c[1])) {
        c[1]["color"] = colors[Math.floor(colors.length * Math.random())];
        persist();
    }
    // console.log("load_c_i", JSON.stringify(c[1]))
    bg = c[1].forgotten ? ' gray' : ' light';
    row = "<button class=contact_picture style='margin-right: 0.75em; background: " + c[1].color + ";'>" + c[1].initial + "</button>";
    row += "<button class='chat_item_button" + bg + "' style='overflow: hidden; width: calc(100% - 4em);' onclick='show_contact_details(\"" + c[0] + "\");'>";
    row += "<div style='white-space: nowrap;'><div style='text-overflow: ellipsis; overflow: hidden;'>" + escapeHTML(c[1].alias) + "</div>";
    row += "<div style='text-overflow: clip; overflow: ellipsis;'><font size=-2>" + c[0] + "</font></div></div></button>";
    // var row  = "<td><button class=contact_picture></button><td style='padding: 5px;'><button class='contact_item_button light w100'>";
    // row += escapeHTML(c[1].alias) + "<br><font size=-2>" + c[0] + "</font></button>";
    // console.log(row);
    item.innerHTML = row;
    document.getElementById('lst:contacts').appendChild(item);
}

function fill_members() {
    var choices = '';
    for (var m in tremola.contacts) {
        choices += '<div style="margin-bottom: 10px;"><label><input type="checkbox" id="' + m;
        choices += '" style="vertical-align: middle;"><div class="contact_item_button light" style="white-space: nowrap; width: calc(100% - 40px); padding: 5px; vertical-align: middle;">';
        choices += '<div style="text-overflow: ellipis; overflow: hidden;">' + escapeHTML(fid2display(m)) + '</div>';
        choices += '<div style="text-overflow: ellipis; overflow: hidden;"><font size=-2>' + m + '</font></div>';
        choices += '</div></label></div>\n';
    }
    document.getElementById('lst:members').innerHTML = choices
    /*
      <div id='lst:members' style="display: none;margin: 10pt;">
        <div style="margin-top: 10pt;"><label><input type="checkbox" id="toggleSwitches2" style="margin-right: 10pt;"><div class="contact_item_button light" style="display: inline-block;padding: 5pt;">Choice1<br>more text</div></label></div>
      </div>
    */
    document.getElementById(myId).checked = true;
    document.getElementById(myId).disabled = true;
}

function show_contact_details(id) {
    if (id == myId) {
        document.getElementById('old_contact_alias_hdr').innerHTML = "Alias: (own name, visible to others)"
    } else {
        document.getElementById('old_contact_alias_hdr').innerHTML = "Alias: (only you can see this alias)"
    }
    var c = tremola.contacts[id];
    new_contact_id = id;
    document.getElementById('old_contact_alias').value = c['alias'];
    var details = '';
    details += '<br><div>IAM-Alias: &nbsp;' + (c.iam != "" ? c.iam : "&mdash;") + '</div>\n';
    details += '<br><div>Shortname: &nbsp;' + id2b32(id) + '</div>\n';
    details += '<br><div style="word-break: break-all;">SSB identity: &nbsp;<tt>' + id + '</tt></div>\n';
    details += '<br><div class=settings style="padding: 0px;"><div class=settingsText>Forget this contact</div><div style="float: right;"><label class="switch"><input id="hide_contact" type="checkbox" onchange="toggle_forget_contact(this);"><span class="slider round"></span></label></div></div>'
    document.getElementById('old_contact_details').innerHTML = details;
    document.getElementById('old_contact-overlay').style.display = 'initial';
    document.getElementById('overlay-bg').style.display = 'initial';
    document.getElementById('hide_contact').checked = c.forgotten;

    document.getElementById('old_contact_alias').focus();
    overlayIsActive = true;
}

function toggle_forget_contact(e) {
    var c = tremola.contacts[new_contact_id];
    c.forgotten = !c.forgotten;
    persist();
    closeOverlay();
    load_contact_list();
}

function save_content_alias() {
    var c = tremola.contacts[new_contact_id];
    var val = document.getElementById('old_contact_alias').value;
    var deleteAlias = false

    val.trim()

    if (val == '') {
        deleteAlias = true
        if (c.iam != "" && new_contact_id != myId) {
            val = c.iam
        } else {
            val = id2b32(new_contact_id);
        }
    }
    var old_alias = c.alias
    c.alias = val;
    c.initial = val.substring(0, 1).toUpperCase();
    c.color = colors[Math.floor(colors.length * Math.random())];

    // update names in connected devices menu
    for (var l in localPeers) {
        if (localPeers[l].alias == old_alias) {
            localPeers[l].alias = val
            refresh_connection_entry(l)
        }
    }

    // share new alias with others via IAM message
    if(new_contact_id == myId) {
        if(deleteAlias) {
            backend("iam " + btoa(""))
            c.iam = ""
        } else {
            backend("iam " + btoa(val))
            c.iam = val
        }
    }

    persist();
    menu_redraw();
    closeOverlay();
}

function new_conversation() {
    // { "alias":"local notes (for my eyes only)", "posts":{}, "members":[myId], "touched": millis }
    var recps = []
    for (var m in tremola.contacts) {
        if (document.getElementById(m).checked)
            recps.push(m);
    }
    if (recps.indexOf(myId) < 0)
        recps.push(myId);
    if (recps.length > 7) {
        launch_snackbar("Too many recipients");
        return;
    }
    var cid = recps2nm(recps)
    if (cid in tremola.chats) {
        if (tremola.chats[cid].forgotten) {
            tremola.chats[cid].forgotten = false;
            load_chat_list(); // refresh
        } else
            launch_snackbar("Conversation already exists");
        return;
    }
    var nm = recps2nm(recps);
    if (!(nm in tremola.chats)) {
        tremola.chats[nm] = {
            "alias": "Unnamed conversation", "posts": {},
            "members": recps, "touched": Date.now(), "timeline": new Timeline()
        };
        persist();
    } else
        tremola.chats[nm]["touched"] = Date.now()
    load_chat_list();
    setScenario("chats")
    curr_chat = nm
    menu_edit_convname()
}

function load_peer_list() {
    var i, lst = '', row;
    for (i in localPeers) {
        var x = localPeers[i], color, row, nm, tmp;
        if (x[1]) color = ' background: var(--lightGreen);'; else color = '';
        tmp = i.split('~');
        nm = '@' + tmp[1].split(':')[1] + '.ed25519'
        if (nm in tremola.contacts)
            nm = ' / ' + tremola.contacts[nm].alias
        else
            nm = ''
        row = "<button class='flat buttontext' style='border-radius: 25px; width: 50px; height: 50px; margin-right: 0.75em;" + color + "'><img src=img/signal.svg style='width: 50px; height: 50px; margin-left: -3px; margin-top: -3px; padding: 0px;'></button>";
        row += "<button class='chat_item_button light' style='overflow: hidden; width: calc(100% - 4em);' onclick='show_peer_details(\"" + i + "\");'>";
        row += "<div style='white-space: nowrap;'><div style='text-overflow: ellipsis; overflow: hidden;'>" + tmp[0].substring(4) + nm + "</div>";
        row += "<div style='text-overflow: clip; overflow: ellipsis;'><font size=-2>" + tmp[1].substring(4) + "</font></div></div></button>";
        lst += '<div style="padding: 0px 5px 10px 5px;">' + row + '</div>';
        // console.log(row)
    }
    document.getElementById('the:connex').innerHTML = lst;
}

function show_peer_details(id) {
    new_contact_id = "@" + id.split('~')[1].substring(4) + ".ed25519";
    // if (new_contact_id in tremola.constacts)
    //  return;
    menu_edit("trust_wifi_peer", "Trust and Autoconnect<br>&nbsp;<br><strong>" + new_contact_id + "</strong><br>&nbsp;<br>Should this WiFi peer be trusted (and autoconnected to)? Also enter an alias for the peer - only you will see this alias", "?")
}

function getUnreadCnt(nm) {
    var c = tremola.chats[nm], cnt = 0;
    for (var p in c.posts) {
        if (c.posts[p].when > c.lastRead)
            cnt++;
    }
    return cnt;
}

function set_chats_badge(nm) {
    var e = document.getElementById(nm + '-badge'), cnt;
    cnt = getUnreadCnt(nm)
    if (cnt == 0) {
        e.style.display = 'none';
        return
    }
    e.style.display = null;
    if (cnt > 9) cnt = ">9"; else cnt = "" + cnt;
    e.innerHTML = cnt
}

// --- util

function unicodeStringToTypedArray(s) {
    var escstr = encodeURIComponent(s);
    var binstr = escstr.replace(/%([0-9A-F]{2})/g, function (match, p1) {
        return String.fromCharCode('0x' + p1);
    });
    return binstr;
}

function toHex(s) {
    return Array.from(s, function (c) {
        return ('0' + (c.charCodeAt(0) & 0xFF).toString(16)).slice(-2);
    }).join('')
}

var b32enc_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

function b32enc_do40bits(b40) {
    var long = 0, s = '';
    for (var i = 0; i < 5; i++) long = long * 256 + b40[i];
    for (var i = 0; i < 8; i++, long /= 32) s = b32enc_map[long & 0x1f] + s;
    return s;
}

function b32encode(bytes) {
    var b32 = '', cnt = bytes.length % 5, buf;
    if (cnt == 0) buf = new Uint8Array(bytes.length);
    else buf = new Uint8Array(bytes.length + 5 - cnt);
    for (var i = 0; i < bytes.length; i++) {
        buf[i] = bytes.charCodeAt(i);
    }
    while (buf.length > 0) {
        b32 += b32enc_do40bits(buf.slice(0, 5));
        buf = buf.slice(5, buf.length);
    }
    if (cnt != 0) {
        cnt = Math.floor(8 * (5 - cnt) / 5);
        b32 = b32.substring(0, b32.length - cnt) + '======'.substring(0, cnt)
    }
    return b32;
}

function id2b32(str) { // derive a shortname from the SSB id
    try {
        var b = atob(str.slice(1, -9)); // atob(str.substr(1, str.length-9));
        b = b32encode(b.slice(0, 7)).substr(0, 10);
        return b.substring(0, 5) + '-' + b.substring(5);
    } catch (err) {
    }
    return '??'
}

function escapeHTML(str) {
    return new Option(str).innerHTML;
}

function recps2nm(rcps) { // use concat of sorted FIDs as internal name for conversation
                          // return "ALL";
    return rcps.sort().join('').replace(/.ed25519/g, '');
}

function recps2display(rcps) {
    if (rcps == null) return 'ALL';
    var lst = rcps.map(function (fid) {
        return fid2display(fid)
    });
    return '[' + lst.join(', ') + ']';
}

function fid2display(fid) {
    var a = '';
    if (fid in tremola.contacts)
        a = tremola.contacts[fid].alias;
    if (a == '')
        a = fid.substring(0, 9);
    return a;
}

function import_id(json_str) {
    var json
    try {
        json = JSON.parse(json_str)
    } catch (e) {
        return false // argument is not a valid json string
    }
    if (Object.keys(json).length != 2 || !('curve' in json) || !('secret' in json)) {
        return false // wrong format
    }

    backend("importSecret " + json['secret'])
    return true
}


// --- Interface to Kotlin side and local (browser) storage

function backend(cmdStr) { // send this to Kotlin (or simulate in case of browser-only testing)
    if (typeof Android != 'undefined') {
        Android.onFrontendRequest(cmdStr);
        return;
    }
    cmdStr = cmdStr.split(' ')
    if (cmdStr[0] == 'ready')
        b2f_initialize('@AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=.ed25519')
    else if (cmdStr[0] == 'exportSecret')
        b2f_showSecret('secret_of_id_which_is@AAAA==.ed25519')
    else if (cmdStr[0] == "wipe") {
        resetTremola()
        location.reload()
    } else if (cmdStr[0] == 'publ:post') {
        var draft = atob(cmdStr[2])
        cmdStr.splice(0, 2)
        console.log("CMD STRING", cmdStr)
        var e = {
            'header': {
                'tst': Date.now(),
                'ref': Math.floor(1000000 * Math.random()),
                'fid': myId
            },
            'confid': {},
            'public': ["TAV", atob(cmdStr[0]), null, Date.now()].concat(args)
        }
        b2f_new_event(e)
    } else if (cmdStr[0] == 'kanban') {
        var prev = cmdStr[2] //== "null" ? null : cmdStr[2]
        if (prev != "null") {
            prev = atob(cmdStr[2])
            prev = prev.split(",").map(atob)
        }
        var args = cmdStr[4]
        if (args != "null") {
            args = atob(cmdStr[4])
            args = args.split(",").map(atob)
        }
        var data = {
            'bid': cmdStr[1],
            'prev': prev,
            'op': cmdStr[3],
            'args': args
        }
        var e = {
            'header': {
                'tst': Date.now(),
                'ref': Math.floor(1000000 * Math.random()),
                'fid': myId
            },
            'confid': {},
            'public': ["KAN", cmdStr[1], prev, cmdStr[3]].concat(args)
        }
        // console.log('e=', JSON.stringify(e))
        b2f_new_event(e)
        console.log(e)
    } else {
        // console.log('backend', JSON.stringify(cmdStr))
    }
}

function resetTremola() { // wipes browser-side content
    tremola = {
        "chats": {},
        "contacts": {},
        "profile": {},
        "id": myId,
        "settings": get_default_settings(),
        "board": {}
    }
    var n = recps2nm([myId])

    //TODO reactivate when encrypted chats are implemented
    /*
    tremola.chats[n] = {
        "alias": "local notes (for my eyes only)", "posts": {}, "forgotten": false,
        "members": [myId], "touched": Date.now(), "lastRead": 0,
        "timeline": new Timeline()
    };
    */

    tremola.chats["ALL"] = {
        "alias": "Public channel", "posts": {},
        "members": ["ALL"], "touched": Date.now(), "lastRead": 0,
        "timeline": new Timeline()
    };
    tremola.contacts[myId] = {"alias": "me", "initial": "M", "color": "#bd7578", "iam": "", "forgotten": false};
    persist();
}

function persist() {
    // console.log(tremola);
    window.localStorage.setItem("tremola", JSON.stringify(tremola));
}

/*
function b2f_local_peer(p, status) { // wireless peer: online, offline, connected, disconnected
    console.log("local peer", p, status);
    if (!(p in localPeers))
        localPeers[p] = [false, false]
    if (status == 'online') localPeers[p][0] = true
    if (status == 'offline') localPeers[p][0] = false
    if (status == 'connected') localPeers[p][1] = true
    if (status == 'disconnected') localPeers[p][1] = false
    if (!localPeers[p][0] && !localPeers[p][1])
        delete localPeers[p]
    load_peer_list()
}
*/


// type: 'udp' or 'ble'
// identifier: unique identifier of the peer
// displayname
// status: 'connected', 'disconnected'

function b2f_ble_enabled() {
    //ble_status = "enabled"
    //TODO update ui
}

function b2f_ble_disabled() {

    for(var p in localPeers) {
        if(localPeers[p].type == "ble") {
            delete localPeers[p]
            refresh_connection_entry(p)
        }
    }
    //ble_status = "disabled"
}

/*
var want = {} // all received want vectors, id: [[want vector], timestamp], want vectors older than 90 seconds are discarded
var max_want = [] // current max vector
var old_curr = [] // own want vector at the time when the maximum want vector was last updated

function b2f_want_update(identifier, wantVector) {

    console.log("b2f received want:", wantVector, "from: ", identifier)

    // remove old want vectors
    var deleted = false;
    for (var id in want) {
        var ts = want[id][1]
        if(Date.now() - ts > 90000) {
            console.log("removed want of", id)
            delete want[id]
            deleted = true
        }

    }

    // if the want vector didn't change, no further updates are required
    if(identifier in want) {
        if( equalArrays(want[identifier][0], wantVector)) {
            console.log("update only")
            want[identifier][1] = Date.now()
            if(!deleted)  //if a want vector was previously removed, the max_want needs to be recalculated otherwise it is just an update without an effect
                return
        }
    }

    want[identifier] = [wantVector, Date.now()]

    // calculate new max want vector
    var all_vectors = Object.values(want).map(val => val[0])
    var new_max_want = all_vectors.reduce((accumulator, curr) => accumulator.len >= curr.len ? accumulator : curr) //return want vector with most entries

    for (var vec of all_vectors) {
        for(var i in vec) {
            if (vec[i] > new_max_want[i])
                new_max_want[i] = vec[i]
        }
    }

    // update
    if (!equalArrays(max_want,new_max_want)) {
        old_curr = want['me'][0]
        max_want = new_max_want
        console.log("new max")
    }

    refresh_connection_progressbar()

    console.log("max:", max_want)
}
*/

function b2f_local_peer_remaining_updates(identifier, remaining) {
    //TODO
}

function b2f_update_progress(min_entries, old_min_entries, old_want_entries, curr_want_entries, max_entries) {
    refresh_connection_progressbar(min_entries, old_min_entries, old_want_entries, curr_want_entries, max_entries)
}

function b2f_local_peer(type, identifier, displayname, status) {
    console.log("incoming displayname:", displayname)
    if (displayname == "null") {
        displayname = identifier
    }

    localPeers[identifier] = {
        'type' : type,
        'name': displayname,
        'status': status,
        'alias': null,
        'remaining': null
    }


    if (tremola != null) // can be the case during the first initialisation
        for (var c in tremola["contacts"]) {
            if (id2b32(c) == displayname) {
                localPeers[identifier].alias = tremola.contacts[c].alias
            }
        }


    console.log("local_peer:", type, identifier, displayname, status)

    if (status == "offline") {
      delete localPeers[identifier]
      //refresh_connection_progressbar()
    }


    if (document.getElementById('connection-overlay').style.display != 'none')
        refresh_connection_entry(identifier)
}

/**
 * This function is called, when the backend received a new log entry and successfully completed the corresponding sidechain.
 * The backend assures, that the log entries are sent to the frontend in the exact same sequential order as in the append-only log.
 *
 * @param {Object} e     Object containing all information of the log_entry.
 * @param {Object} e.hdr Contains basic information about the log entry.
 * @param {number} e.hdr.tst Timestamp at which the message was created. (Number of milliseconds elapsed since midnight at the beginning of January 1970 00:00 UTC)
 * @param {string} e.hdr.ref The message ID of this log entry.
 * @param {string} e.hdr.fid The public key of the author encoded in base64.
 * @param {[]} e.public The payload of the message. The first entry is a String that represents the application to which the message belongs. All additional entries are application-specific parameters.
 *
 */
function b2f_new_in_order_event(e) {

    console.log("b2f inorder event:", JSON.stringify(e.public))

    if (!(e.header.fid in tremola.contacts)) {
        var a = id2b32(e.header.fid);
        tremola.contacts[e.header.fid] = {
            "alias": a, "initial": a.substring(0, 1).toUpperCase(),
            "color": colors[Math.floor(colors.length * Math.random())],
            "iam": "", "forgotten": false
        }
        load_contact_list()
    }

    switch (e.public[0]) {
        case "KAN":
            console.log("New kanban event")
            kanban_new_event(e)
            break
        default:
            return
    }
    persist();
    must_redraw = true;
}

/**
 * This function is invoked whenever the backend receives a new log entry, regardless of whether the associated sidechain is fully loaded or not.
 *
 * @param {Object} e     Object containing all information of the log_entry.
 * @param {Object} e.hdr Contains basic information about the log entry.
 * @param {number} e.hdr.tst Timestamp at which the message was created. (Number of milliseconds elapsed since midnight at the beginning of January 1970 00:00 UTC)
 * @param {string} e.hdr.ref The message ID of this log entry.
 * @param {string} e.hdr.fid The public key of the author encoded in base64.
 * @param {[]} e.public The payload of the logentry, without the content of the sidechain
 *
 */
function b2f_new_incomplete_event(e) {

    if (!(e.header.fid in tremola.contacts)) {
        var a = id2b32(e.header.fid);
        tremola.contacts[e.header.fid] = {
            "alias": a, "initial": a.substring(0, 1).toUpperCase(),
            "color": colors[Math.floor(colors.length * Math.random())],
            "iam": "", "forgotten": false
        }
        load_contact_list()
    }

    switch (e.public[0]) {
        default:
            return
    }
    persist();
    must_redraw = true;


}

/**
 * This function is called, when the backend received a new log entry and successfully completed the corresponding sidechain.
 * This callback does not ensure any specific order; the log entries are forwarded in the order they are received.
 *
 * @param {Object} e     Object containing all information of the log_entry.
 * @param {Object} e.hdr Contains basic information about the log entry.
 * @param {number} e.hdr.tst Timestamp at which the message was created. (Number of milliseconds elapsed since midnight at the beginning of January 1970 00:00 UTC)
 * @param {string} e.hdr.ref The message ID of this log entry.
 * @param {string} e.hdr.fid The public key of the author encoded in base64.
 * @param {[]} e.public The payload of the message. The first entry is a String that represents the application to which the message belongs. All additional entries are application-specific parameters.
 *
 */
function b2f_new_event(e) { // incoming SSB log event: we get map with three entries
                            // console.log('hdr', JSON.stringify(e.header))
    console.log('pub', JSON.stringify(e.public))
    // console.log('cfd', JSON.stringify(e.confid))
    console.log("New Frontend Event: " + JSON.stringify(e.header))

    //add
    if (!(e.header.fid in tremola.contacts)) {
        var a = id2b32(e.header.fid);
        tremola.contacts[e.header.fid] = {
            "alias": a, "initial": a.substring(0, 1).toUpperCase(),
            "color": colors[Math.floor(colors.length * Math.random())],
            "iam": "", "forgotten": false
        }
        load_contact_list()
    }

    if (e.public) {
        if (e.public[0] == 'TAV') { // text and voice
            console.log("new post 0 ", tremola)
            var conv_name = "ALL";
            if (!(conv_name in tremola.chats)) { // create new conversation if needed
                console.log("xx")
                tremola.chats[conv_name] = {
                    "alias": "Public channel X", "posts": {},
                    "members": ["ALL"], "touched": Date.now(), "lastRead": 0,
                    "timeline": new Timeline()
                };
                load_chat_list()
            }
            console.log("new post 1")
            var ch = tremola.chats[conv_name];
            if (ch.timeline == null)
                ch["timeline"] = new Timeline();
            console.log("new post 1 ", ch)
            if (!(e.header.ref in ch.posts)) { // new post
                var a = e.public;
                // var d = new Date(e.header.tst);
                // d = d.toDateString() + ' ' + d.toTimeString().substring(0,5);
                // var txt = null;
                // if (a[1] != null)
                //   txt = a[1];
                var p = {
                    "key": e.header.ref, "from": e.header.fid, "body": a[1],
                    "voice": a[2], "when": a[3] * 1000
                };
                console.log("new post 2 ", p)
                console.log("time: ", a[3])
                ch["posts"][e.header.ref] = p;
                if (ch["touched"] < e.header.tst)
                    ch["touched"] = e.header.tst
                if (curr_scenario == "posts" && curr_chat == conv_name) {
                    load_chat(conv_name); // reload all messages (not very efficient ...)
                    ch["lastRead"] = Date.now();
                }
                set_chats_badge(conv_name)
            } else {
                console.log("known already?")
            }
            // if (curr_scenario == "chats") // the updated conversation could bubble up
            load_chat_list();
        } else if (e.public[0] == "KAN") { // Kanban board event
        } else if (e.public[0] == "IAM") {
            var contact = tremola.contacts[e.header.fid]
            var old_iam = contact.iam
            var old_alias = contact.alias

            contact.iam = e.public[1]

            if ((contact.alias == id2b32(e.header.fid) || contact.alias == old_iam)) {
                contact.alias = e.public[1] == "" ? id2b32(e.header.fid) : e.public[1]
                contact.initial = contact.alias.substring(0, 1).toUpperCase()
                load_contact_list()
                load_board_list()

                // update names in connected devices menu
                for (var l in localPeers) {
                    if (localPeers[l].alias == old_alias) {

                        localPeers[l].alias = contact.alias
                        refresh_connection_entry(l)
                    }
                }
            }

        }
        persist();
        must_redraw = true;
    }
}

function b2f_new_contact(fid) {
    if ((fid in tremola.contacts)) // do not overwrite existing entry
        return
    var id = id2b32(fid);
    tremola.contacts[fid] = {
        "alias": id, "initial": id.substring(0, 1).toUpperCase(),
        "color": colors[Math.floor(colors.length * Math.random())],
        "iam": "", "forgotten": false
    };
    persist()
    load_contact_list();
}

function b2f_new_voice(voice_b64) {
    new_voice_post(voice_b64)
}

function b2f_showSecret(json) {
    //setScenario(prev_scenario);
    generateQR(json)
}

function b2f_new_image_blob(ref) {
    console.log("new image: ", ref);
    curr_img_candidate = ref;
    ref = ref.replace(new RegExp('/'), "_");
    ref = "http://appassets.androidplatform.net/blobs/" + ref;
    ref = "<object type='image/jpeg' data='" + ref + "' style='width: 100%; height: 100%; object-fit: scale-down;'></object>"
    document.getElementById('image-preview').innerHTML = ref
    document.getElementById('image-caption').value = '';
    var s = document.getElementById('image-overlay').style;
    s.display = 'initial';
    s.height = '80%'; // 0.8 * docHeight;
    document.getElementById('overlay-bg').style.display = 'initial';
    overlayIsActive = true;
}

function b2f_initialize(id) {
    myId = id
    if (window.localStorage.tremola) {
        tremola = JSON.parse(window.localStorage.getItem('tremola'));

        if (tremola != null && id != tremola.id) // check for clash of IDs, erase old state if new
            tremola = null;
    } else
        tremola = null;
    if (tremola == null) {
        resetTremola();
        console.log("reset tremola")
    }
    if (typeof Android == 'undefined')
        console.log("loaded ", JSON.stringify(tremola))
    if (!('settings' in tremola))
        tremola.settings = {}
    var nm, ref;
    for (nm in tremola.settings)
        setSetting(nm, tremola.settings[nm])
    load_chat_list()
    load_contact_list()
    load_board_list()

    closeOverlay();
    setScenario('chats');
    // load_chat("ALL");
}

// --- eof
