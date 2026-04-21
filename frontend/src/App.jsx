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
    backgroundColor: '#f5f4ed' // Parchment
  },
  nav: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)',
    borderBottom: '1px solid #f0eee6', // Border Cream
    boxShadow: 'rgba(0, 0, 0, 0.05) 0px 4px 24px', // Whisper shadow
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
    fontSize: '25.6px', // Subhead Small
    fontWeight: '500',
    fontFamily: 'Georgia, serif', // Anthropic Serif fallback
    color: '#141413', // Near Black
    lineHeight: '1.2'
  },
  navRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  },
  adminLink: {
    textDecoration: 'none'
  },
  adminButton: {
    padding: '8px 16px',
    backgroundColor: '#e8e6dc', // Warm Sand
    color: '#4d4c48', // Charcoal Warm
    borderRadius: '8px', // Comfortable
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
    border: 'none',
    boxShadow: '0px 0px 0px 1px #d1cfc5' // Ring shadow
  },
  badge: {
    padding: '6px 12px',
    backgroundColor: '#c96442', // Terracotta Brand
    color: '#faf9f5', // Ivory
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
    backgroundColor: '#30302e', // Dark Surface
    backdropFilter: 'blur(10px)',
    padding: '20px',
    textAlign: 'center',
    borderTop: '1px solid #30302e'
  },
  footerText: {
    color: '#b0aea5', // Warm Silver
    fontSize: '14px',
    margin: 0
  }
}

export default App
