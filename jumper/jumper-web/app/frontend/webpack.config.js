var path = require('path')
var webpack = require('webpack')

module.exports = {
  entry: './src/main.js',
  output: {
    path: path.resolve(__dirname, '../static/dist'),
    publicPath: '/static/dist/',
    filename: 'build.js'
  },

  module: {
    rules: [
         {
        test: /\.(gif|jpg|png|woff|svg|eot|ttf)\??.*$/,
        loader: 'url-loader?limit=100000'
      },

      {
        test: /\.css$/, // Only .css files
        loader: 'style-loader!css-loader' // Run both loaders
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
        options: {
          loaders: {
          }
          // other vue-loader options go here
        }
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      // {
      //   test: /\.(png|jpg|gif|svg)$/,
      //   loader: 'file-loader',
      //   options: {
      //     name: '[name].[ext]?[hash]'
      //   }
      // }
    ]
  },
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.common.js'
      // Semantic-UI
//      'semantic': path.resolve(__dirname, '../node_modules/semantic-ui-css/semantic.min.js')
    }
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": "jquery",
      "jquery": "jquery",
      "vue": "vue",
      // Semantic-UI
      semantic: "semantic-ui-css",
      Semantic: "semantic-ui-css",
      "semantic-ui": "semantic-ui-css"
    })
  ],
  devServer: {
    historyApiFallback: true,
    noInfo: true,
    proxy: [
      {
        context: ["/logout", "/login"],
        target: 'http://127.0.0.1:8080/',
        secure: false
      },
      {
        context: ["/api/**"],
        target: 'http://127.0.0.1:8080/',
        secure: false
      },
    ],
  },
  performance: {
    hints: false
  },
  devtool: '#eval-source-map'
};


if (process.env.NODE_ENV === 'production') {
  module.exports.devtool = '#source-map';
  // http://vue-loader.vuejs.org/en/workflow/production.html
  module.exports.plugins = (module.exports.plugins || []).concat([
    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: '"production"'
      }
    }),
    new webpack.optimize.UglifyJsPlugin({
      sourceMap: true,
      compress: {
        warnings: false
      }
    }),
    new webpack.LoaderOptionsPlugin({
      // minimize: true
    })
  ])
}
