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
import { TimelineEditorPage } from './pages/TimelineEditorPage'
import AdminDashboard from './pages/AdminDashboard'

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
              <Link to="/admin" style={styles.adminLink}>
                <span style={styles.adminButton}>⚙️ 管理后台</span>
              </Link>
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
            <Route path="/timeline-editor/:sceneId" element={<TimelineEditorPage />} />
            <Route path="/admin" element={<AdminDashboard />} />
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
    backgroundColor: '#FAF9F6'
  },
  nav: {
    backgroundColor: '#FFFFFF',
    borderBottom: '1px solid #E8E6E0',
    position: 'sticky',
    top: 0,
    zIndex: 1000
  },
  navContainer: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: '72px'
  },
  navLink: {
    textDecoration: 'none',
    color: 'inherit'
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  },
  logoIcon: {
    fontSize: '28px',
    lineHeight: '1'
  },
  navTitle: {
    margin: '0',
    fontSize: '18px',
    fontWeight: '300',
    fontFamily: 'Georgia, "Times New Roman", serif',
    color: '#2C2416',
    letterSpacing: '-0.01em'
  },
  navRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px'
  },
  adminLink: {
    textDecoration: 'none'
  },
  adminButton: {
    padding: '10px 20px',
    backgroundColor: 'transparent',
    color: '#2C2416',
    border: '1px solid #E8E6E0',
    fontSize: '12px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },
  badge: {
    padding: '6px 14px',
    backgroundColor: '#2C2416',
    color: '#FAF9F6',
    fontSize: '10px',
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: '0.12em'
  },
  main: {
    flex: 1,
    padding: '0',
    width: '100%'
  },
  footer: {
    backgroundColor: '#2C2416',
    padding: '32px 24px',
    textAlign: 'center',
    borderTop: '1px solid #2C2416'
  },
  footerText: {
    color: '#8B7355',
    fontSize: '12px',
    margin: 0,
    letterSpacing: '0.05em'
  }
}

export default App
