import LineChart from './charJS/line'

export default LineChart.extend({
  props: ['data'],

  mounted () {
    let data = {};
    let label = [];
    let labels = [];

    for (var key in this.data) {
      let list = [];
      if (key != 'backend_online') {
        label.push(key);
      }
      this.data[key].forEach(function(dict) {
        list.push(dict.value)});
      data[key] = list;
    }
    this.data[label[0]].forEach(function(dict){
        labels.push(dict['timestamp'])
    });
    this.renderChart({
      labels: labels,
        datasets: [
          {
              label: '上海在线用户',
              backgroundColor: 'rgba(255,50,50,0.2)',
              // backgroundColor: 'rgba(0,0,0,0)',
              borderColor: 'rgba(255,50,50,0.4)',
              border: '0px',
              data: data['dp_user_online']
          },
          {
              label: '北京在线用户',
              backgroundColor: 'rgba(50,155,155,0.2)',
              // backgroundColor: 'rgba(0,0,0,0)',
              borderColor: 'rgba(50,155,155,0.4)',
              border: '0px',
              data: data['mt_user_online']
          },
          {
              label: '上海在线会话',
              backgroundColor: 'rgba(10,220,25,0.2)',
              // backgroundColor: 'rgba(0,0,0,0)',
              // borderColor: 'green',
              borderColor: 'rgba(10,220,25,0.4)',
              border: '0px',
              data: data['dp_session_online']
          },
          {
              label: '北京在线会话',
              backgroundColor: 'rgba(200,100,100,0.2)',
              // backgroundColor: 'rgba(0,0,0,0)',
              // borderColor: 'green',
              borderColor: 'rgba(200,100,100,0.4)',
              border: '0px',
              data: data['mt_session_online']
          },
          // {
          //     label: '上海在线会话',
          //     backgroundColor: 'rgba(0,22,250,0.2)',
          //     // backgroundColor: 'rgba(0,0,0,0)',
          //     // borderColor: 'green',
          //     borderColor: 'rgba(0,22,250,0.4)',
          //     border: '0px',
          //     data: data['dp_session_online']
          // },
      ]
    }, {responsive: true, maintainAspectRatio: false})
  }
})
