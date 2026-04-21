/**
 * input: 依赖 React、React Router 和后端 API。
 * output: 向外提供管理后台主页面。
 * pos: 位于页面层，负责管理后台整体布局和导航。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import ProjectsManager from '../components/ProjectsManager'
import JobsManager from '../components/JobsManager'
import LogsViewer from '../components/LogsViewer'
import ResourcesManager from '../components/ResourcesManager'

const API_BASE = 'http://localhost:8000'

function AdminDashboard() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalJobs: 0,
    runningJobs: 0,
    completedJobs: 0,
    failedJobs: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      // 这里可以添加统计 API 调用
      // 暂时使用模拟数据
      setStats({
        totalProjects: 0,
        totalJobs: 0,
        runningJobs: 0,
        completedJobs: 0,
        failedJobs: 0
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab stats={stats} />
      case 'projects':
        return <ProjectsTab />
      case 'jobs':
        return <JobsTab />
      case 'logs':
        return <LogsTab />
      case 'resources':
        return <ResourcesTab />
      default:
        return <OverviewTab stats={stats} />
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <h2 style={styles.sidebarTitle}>管理后台</h2>
        </div>
        <nav style={styles.nav}>
          <button
            style={{...styles.navItem, ...(activeTab === 'overview' ? styles.navItemActive : {})}}
            onClick={() => setActiveTab('overview')}
          >
            📊 概览
          </button>
          <button
            style={{...styles.navItem, ...(activeTab === 'projects' ? styles.navItemActive : {})}}
            onClick={() => setActiveTab('projects')}
          >
            📁 项目管理
          </button>
          <button
            style={{...styles.navItem, ...(activeTab === 'jobs' ? styles.navItemActive : {})}}
            onClick={() => setActiveTab('jobs')}
          >
            ⚙️ 任务管理
          </button>
          <button
            style={{...styles.navItem, ...(activeTab === 'logs' ? styles.navItemActive : {})}}
            onClick={() => setActiveTab('logs')}
          >
            📝 日志查看
          </button>
          <button
            style={{...styles.navItem, ...(activeTab === 'resources' ? styles.navItemActive : {})}}
            onClick={() => setActiveTab('resources')}
          >
            💾 资源管理
          </button>
        </nav>
        <div style={styles.sidebarFooter}>
          <button
            style={styles.backButton}
            onClick={() => navigate('/')}
          >
            ← 返回前台
          </button>
        </div>
      </div>
      <div style={styles.main}>
        {renderContent()}
      </div>
    </div>
  )
}

// 概览标签页
function OverviewTab({ stats }) {
  return (
    <div style={styles.content}>
      <h1 style={styles.pageTitle}>系统概览</h1>
      <div style={styles.statsGrid}>
        <StatCard title="总项目数" value={stats.totalProjects} icon="📁" color="#667eea" />
        <StatCard title="总任务数" value={stats.totalJobs} icon="⚙️" color="#764ba2" />
        <StatCard title="运行中" value={stats.runningJobs} icon="🔄" color="#f59e0b" />
        <StatCard title="已完成" value={stats.completedJobs} icon="✅" color="#10b981" />
        <StatCard title="失败" value={stats.failedJobs} icon="❌" color="#ef4444" />
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, color }) {
  return (
    <div style={{...styles.statCard, borderLeft: `4px solid ${color}`}}>
      <div style={styles.statIcon}>{icon}</div>
      <div style={styles.statContent}>
        <div style={styles.statTitle}>{title}</div>
        <div style={styles.statValue}>{value}</div>
      </div>
    </div>
  )
}

// 项目管理标签页
function ProjectsTab() {
  return (
    <div style={styles.content}>
      <h1 style={styles.pageTitle}>项目管理</h1>
      <ProjectsManager />
    </div>
  )
}

// 任务管理标签页
function JobsTab() {
  return (
    <div style={styles.content}>
      <h1 style={styles.pageTitle}>任务管理</h1>
      <JobsManager />
    </div>
  )
}

// 日志查看标签页
function LogsTab() {
  return (
    <div style={styles.content}>
      <h1 style={styles.pageTitle}>日志查看</h1>
      <LogsViewer />
    </div>
  )
}

// 资源管理标签页
function ResourcesTab() {
  return (
    <div style={styles.content}>
      <h1 style={styles.pageTitle}>资源管理</h1>
      <ResourcesManager />
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#f5f4ed' // Parchment
  },
  sidebar: {
    width: '260px',
    backgroundColor: '#141413', // Near Black
    color: '#faf9f5', // Ivory
    display: 'flex',
    flexDirection: 'column',
    boxShadow: 'rgba(0, 0, 0, 0.05) 0px 4px 24px'
  },
  sidebarHeader: {
    padding: '24px 20px',
    borderBottom: '1px solid #30302e' // Dark Surface
  },
  sidebarTitle: {
    margin: 0,
    fontSize: '20.8px', // Feature Title
    fontWeight: '500',
    fontFamily: 'Georgia, serif' // Anthropic Serif fallback
  },
  nav: {
    flex: 1,
    padding: '20px 0'
  },
  navItem: {
    width: '100%',
    padding: '12px 20px',
    border: 'none',
    backgroundColor: 'transparent',
    color: '#b0aea5', // Warm Silver
    textAlign: 'left',
    fontSize: '15px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  navItemActive: {
    backgroundColor: 'rgba(201, 100, 66, 0.15)', // Terracotta with transparency
    color: '#faf9f5', // Ivory
    borderLeft: '3px solid #c96442' // Terracotta Brand
  },
  sidebarFooter: {
    padding: '20px',
    borderTop: '1px solid #30302e' // Dark Surface
  },
  backButton: {
    width: '100%',
    padding: '10px',
    border: '1px solid #30302e',
    backgroundColor: 'transparent',
    color: '#b0aea5', // Warm Silver
    borderRadius: '8px', // Comfortable
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.2s',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  main: {
    flex: 1,
    overflow: 'auto',
    backgroundColor: '#f5f4ed' // Parchment
  },
  content: {
    padding: '40px'
  },
  pageTitle: {
    margin: '0 0 30px 0',
    fontSize: '32px', // Subhead
    fontWeight: '500',
    fontFamily: 'Georgia, serif', // Anthropic Serif fallback
    color: '#141413', // Near Black
    lineHeight: '1.1'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    marginTop: '20px'
  },
  statCard: {
    backgroundColor: '#faf9f5', // Ivory
    padding: '20px',
    borderRadius: '12px', // Generous
    border: '1px solid #f0eee6', // Border Cream
    boxShadow: 'rgba(0, 0, 0, 0.05) 0px 4px 24px', // Whisper shadow
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    transition: 'all 0.2s'
  },
  statIcon: {
    fontSize: '32px'
  },
  statContent: {
    flex: 1
  },
  statTitle: {
    fontSize: '14px',
    color: '#5e5d59', // Olive Gray
    marginBottom: '4px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  statValue: {
    fontSize: '28px',
    fontWeight: '500',
    color: '#141413', // Near Black
    fontFamily: 'Georgia, serif' // Anthropic Serif fallback
  },
  placeholder: {
    color: '#87867f', // Stone Gray
    fontSize: '16px'
  }
}

export default AdminDashboard
