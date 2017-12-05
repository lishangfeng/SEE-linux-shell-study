import Terminal from './../terminal/term.js';



// 验证参数
function checkURL(query_string, options) {

    // 获取要登陆的指定主机名; 验证uuid
    try{
        options['uuid'] = query_string.split("uuid=")[1].split("&")[0]
    }catch (e) {
        options['uuid'] = ''
    }
    try{
        options['user'] = query_string.split("user=")[1].split("&")[0]
    }catch (e) {
        options['user'] = ''
    }
    try{
        options['host'] = query_string.split("host=")[1].split("&")[0]
    }catch (e) {
        options['host'] = ''
    }
    try{
        options['channel_id'] = query_string.split("channel_id=")[1].split("&")[0]
    }catch (e) {
        options['channel_id'] = ''
    }
    try{
        options['start'] = query_string.split("start=")[1].split("&")[0]
    }catch (e) {
        options['start'] = ''
    }
    try{
        options['end'] = query_string.split("end=")[1].split("&")[0]
    }catch (e) {
        options['end'] = ''
    }
}



// websocket 连接
function WSSHClient() {
}
WSSHClient.prototype._generateEndpoint = function (options) {
    let protocol;
    if (window.location.protocol == 'https:') {
        protocol = 'wss://';
    } else {
        protocol = 'ws://';
    }
    let endpoint = 'wss://' + options['socket_server'] + '/ws/video?user=' + options['user'] + '&uuid=' + options['uuid']
                                                      + '&channel_id=' + options['channel_id'] + '&host=' + options['host']
                                                      + '&start=' + options['start'] + '&end=' + options['end'];
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
    rowHeight = 30;
    colWidth = 120;

    let term = new Terminal({
        rows: rowHeight,
        cols: colWidth,
        useStyle: true,
        screenKeys: true
    });

    // 若携带uuid参数，则调用web-socket服务; 否则，返回'缺少参数'错误
    if (options['uuid'] != '' && options['channel_id'] != '' && options['user'] != '' && options['host'] != '') {
        client = new WSSHClient();
    }
    else {
        client = false
    }
    term.open();
    term.on('data', function (data) {
        client.send(data)
    });
    $('.terminal').detach().appendTo('#term');
    if (options['uuid'] == '' || options['channel_id'] == '' || options['user'] == ''|| options['host'] == '') {
        term.write('缺少参数，已放弃回放录像...');
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
            if (data.indexOf('?1049') != -1) {
                options['vim'] = !options['vim'];
                if (options['vim']) {
                    term.resize(120, 60);
                } else {
                    term.resize(120, 30);
                }
            }
            term.write(data);
        }
    }));
    return {'term': term, 'client': client};
}



// js页面入口
$(document).ready(function () {
    let query_string = window.location.hash.substr(1), options = {};
    options['vim'] = false;
    let play = true;
    let rate = 1;

    // websocket服务域名
    options['socket_server'] = window.location.host.split(':')[0];
    // options['socket_server'] = '10.72.206.245' + ':8000';

    checkURL(query_string, options);
    $('#ssh').show();
    let term_client = openTerminal(options);
    $('#playBackwardRate').click(function () {
        if (rate > 1) {rate = rate - 1;}
        else {rate = 1}
        if (term_client.client){
            term_client.client.send({'rate': rate});
        }
    });
    $('#playForwardRate').click(function () {
        if (rate < 10) {rate = rate + 1;}
        else {rate = 10}
        if (term_client.client){
            term_client.client.send({'rate': rate});
        }
    });
    $('#Play').click(function () {
        play = !play;
        if (term_client.client){
            term_client.client.send({'play': play});
        }
    });
    $('#Skip').click(function () {
        if (term_client.client){
            term_client.client.send({'skip': true});
        }
    });
    let last_start = options['start'];
    let last_end = options['end'];
    $('#timeLine').click(function () {
        let start =  Date.parse($('#startTime').val());
        let end =  Date.parse($('#endTime').val());

        if ((end != options['end'] && end != last_end) || (start != options['start'] && start != last_start)) {
            last_end = end; last_start = start;
            if (term_client.client){
                term_client.client.send({'start': start, 'end': end, 'reset':true});
                if (options['vim']) {
                    options['vim'] = false;
                    term_client.term.resize(120, 30);
                }
            }
        }
    });
});
