import path from 'path';

export default {
  mode: 'development',
  entry: './src/index.js',
  output: {
    path: path.resolve(process.cwd(), 'dist'),
    filename: 'bundle.js',
    publicPath: '/'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx', '.json'],
    extensionAlias: {
      '.js': ['.js', '.jsx']
    }
  },
  devServer: {
    static: {
      directory: path.join(process.cwd(), 'public'),
    },
    port: 3002,
    open: true,
    hot: true,
    historyApiFallback: true,
    proxy: [
      {
        context: ['/api'],
        target: 'http://localhost:5001',
        secure: false,
        changeOrigin: true
      }
    ],
    devMiddleware: {
      publicPath: '/'
    }
  }
};