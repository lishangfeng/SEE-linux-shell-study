import Terminal from './term.js';



// 验证参数
function checkURL(query_string, options) {

    // 获取要登陆的指定主机名; 验证uuid
    try{
        options['uuid'] = query_string.split("uuid=")[1].split("&")[0]
    }catch (e) {
        options['uuid'] = ''
    }
    try{
        options['host_name'] = query_string.split("host_name=")[1].split("&")[0]
    }catch (e) {
        options['host_name'] = ''
    }
}



// websocket 连接
function WSSHClient() {
}
WSSHClient.prototype._generateEndpoint = function (options) {
    let protocol;
    // if (window.location.protocol == 'https:') {
    //     protocol = 'wss://';
    // } else {
    //     protocol = 'ws://';
    // }
    let endpoint = 'wss://' + options['socket_server'] + '/ws/terminal?user_name=' + options['loginName'] + '&uuid=' + options['uuid'];
    return endpoint;
};

WSSHClient.prototype.connect = function (options) {
    let endpoint = this._generateEndpoint(options);

    if (window.WebSocket) {
        this._connection = new WebSocket(endpoint);
    }
    else if (window.MozWebSocket) {
        this._connection = MozWebSocket(endpoint);
    }
    else {
        options.onError('WebSocket Not Supported');
        return;
    }

    this._connection.onopen = function () {
        options.onConnect();
    };

    this._connection.onmessage = function (evt) {
        try {
            options.onData(evt.data);
        } catch (e) {
            let data = JSON.parse(evt.data.toString());
            options.onError(data.error);
        }
    };

    this._connection.onclose = function (evt) {
        options.onClose();
    };
};

WSSHClient.prototype.send = function (data) {
    this._connection.send(JSON.stringify({'data': data}));
};



// 终端展示
function openTerminal(options) {
    // 打开终端界面
    let client, rowHeight, colWidth;
    rowHeight = 35;
    try {
        colWidth = localStorage.getItem('term-col');
    } catch (err) {
        colWidth = 120
    }
    if (colWidth) {
    } else {
        colWidth = 120
    }

    let term = new Terminal({
        rows: rowHeight,
        cols: colWidth,
        useStyle: true,
        screenKeys: true
    });

    // 若携带uuid参数，则调用web-socket服务; 否则，返回'缺少参数'错误
    if (options['uuid'] == '') {
         if (options['host_name'] == '') {
            let datas = {'user_name': options['loginName'], 'origin': "jumper", 'host_name': 'll'};
            $.ajax({
                  type:"post",
                  url:"/api/web/code",
                  async: false,
                  data: JSON.stringify(datas),
                  dataType:"json",
                  cache: false,
                  contentType:"application/json; utf-8",
                  success: function (data) {
                        options['uuid'] = data.result.uuid;
                        client = new WSSHClient();
                  }
            });
        }
        else {
            client = false
         }
    }
    else {
        client = new WSSHClient();
    }
    term.open();
    term.on('data', function (data) {
        client.send(data)
    });
    $('.terminal').detach().appendTo('#term');
    if (options['uuid'] == '') {
        term.write('缺少参数，已放弃登陆跳板机...');
        return {'term': term, 'client': client};
    }
    client.connect($.extend(options, {
        onError: function (error) {
            term.write('Error: ' + error + '\r\n');
        },
        onConnect: function () {
            // Erase our connecting message
            client.send({'resize': {'rows': rowHeight, 'cols': colWidth}});
            term.write('\r');
        },
        onClose: function () {
            term.write('Connection Reset By Peer');
        },
        onData: function (data) {
            //若携带host_name参数，
            if (options['host_name'] != ''){
                client.send('ssh ' + options['host_name'] + '\r');
                options['host_name'] = '';
            }
            term.write(data);
        }
    }));
    return {'term': term, 'client': client};
}



// js页面入口
$(document).ready(function () {
    let query_string = window.location.hash.substr(1), options = {};
    let show = false;
    $(".termChangBar").slideUp();

    // websocket服务域名
    options['socket_server'] = window.location.host.split(':')[0];
    // options['socket_server'] = window.location.host.split(':')[0] + ':8080';

    $.get('/api/user/my', function(data){
        options['loginName'] = data.result.login_name;
        checkURL(query_string, options);
        $('#ssh').show();
        let term_client = openTerminal(options);
       try {
           $('#term-col')[0].value = localStorage.getItem('term-col');
       } catch (err) {
           $('#term-col')[0].value = 120;
       }
       $('#col-row').click(function () {
           let row = 35;
           let col = $('#term-col').val();
           if (col == ''){col = 120;}   else {parseInt(col)}
           localStorage.setItem('term-col', col);
           term_client.term.resize(col, row);
           if (term_client.client){
               term_client.client.send({'resize': {'rows': row, 'cols': col}});
           }
           $('#ssh').show();
           show = false;
           $(".termChangBar").slideUp();
       });
        $('#winShow').click(function () {
            show = !show;
            if (show) {
                $(".termChangBar").slideDown();
            }
            else {
                $(".termChangBar").slideUp();
            }
        });
    });
});
