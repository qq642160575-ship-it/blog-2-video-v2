/**
 * input: 依赖 React Router 和页面组件。
 * output: 向外提供前端整体布局与路由树。
 * pos: 位于前端壳层，负责组织页面导航。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import CreateProject from './pages/CreateProject'
import GenerationProgress from './pages/GenerationProgress'
import Result from './pages/Result'
import EditScene from './pages/EditScene'

function App() {
  return (
    <Router>
      <div style={styles.app}>
        <nav style={styles.nav}>
          <div style={styles.navContainer}>
            <Link to="/" style={styles.navLink}>
              <div style={styles.logo}>
                <span style={styles.logoIcon}>🎬</span>
                <h2 style={styles.navTitle}>博文视频生成器</h2>
              </div>
            </Link>
            <div style={styles.navRight}>
              <span style={styles.badge}>AI Powered</span>
            </div>
          </div>
        </nav>

        <main style={styles.main}>
          <Routes>
            <Route path="/" element={<CreateProject />} />
            <Route path="/generate/:projectId" element={<GenerationProgress />} />
            <Route path="/result/:projectId" element={<Result />} />
            <Route path="/edit-scene/:sceneId" element={<EditScene />} />
          </Routes>
        </main>

        <footer style={styles.footer}>
          <p style={styles.footerText}>
            © 2026 博文视频生成系统 | Powered by AI
          </p>
        </footer>
      </div>
    </Router>
  )
}

const styles = {
  app: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  nav: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
    position: 'sticky',
    top: 0,
    zIndex: 1000
  },
  navContainer: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  navLink: {
    textDecoration: 'none',
    color: 'inherit'
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  logoIcon: {
    fontSize: '32px'
  },
  navTitle: {
    margin: '0',
    padding: '20px 0',
    fontSize: '24px',
    fontWeight: 'bold',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text'
  },
  navRight: {
    display: 'flex',
    alignItems: 'center'
  },
  badge: {
    padding: '6px 12px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.5px'
  },
  main: {
    flex: 1,
    padding: '40px 20px',
    maxWidth: '1200px',
    width: '100%',
    margin: '0 auto'
  },
  footer: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    padding: '20px',
    textAlign: 'center',
    borderTop: '1px solid rgba(255, 255, 255, 0.2)'
  },
  footerText: {
    color: 'white',
    fontSize: '14px',
    margin: 0
  }
}

export default App
