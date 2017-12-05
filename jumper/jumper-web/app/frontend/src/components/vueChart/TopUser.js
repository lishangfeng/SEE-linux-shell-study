import Bar from './charJS/bar.js'


export default Bar.extend({
    props: ['label', 'data'],

    mounted () {
    // Overwriting base render method with actual data.
    this.renderChart({
        labels: this.label,
        datasets: [
        {
            label: '近一周登陆服务器次数',
            // backgroundColor: '#f87979',
            backgroundColor: '#f09090',
            width: '25px',
            // fillColor: "rgba(151,187,205,0.2)",
            // strokeColor: "rgba(151,187,205,1)",
            // pointColor: "rgba(151,187,205,1)",
            // pointStrokeColor: "#fff",
            // backgroundColor: 'teal',
            data: this.data,
        }
      ]
    })
  }
})