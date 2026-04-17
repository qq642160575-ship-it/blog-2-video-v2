/**
 * input: 依赖 React、ReactDOM 和 App 组件。
 * output: 向外提供前端应用挂载入口。
 * pos: 位于前端入口层，负责启动前端应用。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
