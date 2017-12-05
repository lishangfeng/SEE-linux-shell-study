import Vue from 'vue'
import Chart from 'chart.js'
import { mergeOptions } from '../help.js'

export default Vue.extend({
  render: function (createElement) {
    return createElement(
      'div',
      [
        createElement(
          'canvas', {
            attrs: {
              id: this.chartId,
              width: this.width,
              height: this.height,
            },
            ref: 'canvas'
          }
        )
      ]
    )
  },

  props: {
    chartId: {
      default: 'line-chart',
      type: String
    },
    width: {
      default: 400,
      type: Number
    },
    height: {
      default: 400,
      type: Number
    }
  },

  data () {
    return {
      defaultOptions: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            },
            gridLines: {
              display: true
            }
          }],
          xAxes: [ {
            gridLines: {
              display: true
            }
          }]
        }
      }
    }
  },

  methods: {
    renderChart (data, options) {
      let chartOptions = mergeOptions(this.defaultOptions, options);

      this._chart = new Chart(
        this.$refs.canvas.getContext('2d'), {
          type: 'line',
          data: data,
          options: chartOptions
        }
      );
      this._chart.generateLegend()
    }
  },
  beforeDestroy () {
    this._chart.destroy()
  }
})