/**
 * Editorial Studio Dashboard - 管理后台
 * 设计理念：Editorial Studio 美学 - 温暖奶油色调 + 衬线字体 + 琥珀色点缀
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
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    loadStats()
    setTimeout(() => setMounted(true), 100)
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/stats/overview`)
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
      setStats({
        totalProjects: 0,
        totalJobs: 0,
        runningJobs: 0,
        completedJobs: 0,
        failedJobs: 0
      })
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab stats={stats} loading={loading} />
      case 'projects':
        return <ProjectsTab />
      case 'jobs':
        return <JobsTab />
      case 'logs':
        return <LogsTab />
      case 'resources':
        return <ResourcesTab />
      default:
        return <OverviewTab stats={stats} loading={loading} />
    }
  }

  return (
    <div style={styles.container}>
      {/* 侧边栏 */}
      <aside style={{
        ...styles.sidebar,
        transform: mounted ? 'translateX(0)' : 'translateX(-100%)',
        opacity: mounted ? 1 : 0
      }}>
        {/* Logo 区域 */}
        <div style={styles.sidebarHeader}>
          <div style={styles.logoContainer}>
            <div style={styles.logoIcon}>🎬</div>
            <div>
              <h2 style={styles.sidebarTitle}>ADMIN</h2>
              <p style={styles.sidebarSubtitle}>Management Console</p>
            </div>
          </div>
        </div>

        {/* 导航菜单 */}
        <nav style={styles.nav}>
          {[
            { id: 'overview', icon: '01', label: 'Overview', subtitle: '概览' },
            { id: 'projects', icon: '02', label: 'Projects', subtitle: '项目' },
            { id: 'jobs', icon: '03', label: 'Jobs', subtitle: '任务' },
            { id: 'logs', icon: '04', label: 'Logs', subtitle: '日志' },
            { id: 'resources', icon: '05', label: 'Resources', subtitle: '资源' }
          ].map((item, index) => (
            <NavButton
              key={item.id}
              {...item}
              active={activeTab === item.id}
              onClick={() => setActiveTab(item.id)}
              delay={index * 50}
              mounted={mounted}
            />
          ))}
        </nav>

        {/* 底部返回按钮 */}
        <div style={styles.sidebarFooter}>
          <button
            style={styles.backButton}
            onClick={() => navigate('/')}
          >
            <span style={styles.backIcon}>←</span>
            <span>返回前台</span>
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main style={styles.main}>
        <div style={{
          ...styles.mainContent,
          opacity: mounted ? 1 : 0,
          transform: mounted ? 'translateY(0)' : 'translateY(20px)'
        }}>
          {renderContent()}
        </div>
      </main>
    </div>
  )
}

// 导航按钮组件
function NavButton({ id, icon, label, subtitle, active, onClick, delay, mounted }) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <button
      style={{
        ...styles.navItem,
        ...(active ? styles.navItemActive : {}),
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateX(0)' : 'translateX(-20px)',
        transitionDelay: `${delay}ms`,
        backgroundColor: isHovered && !active ? '#F5F3EE' :
                         active ? '#FAF9F6' : 'transparent',
        borderColor: active ? '#D4A574' : '#E8E6E0'
      }}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span style={styles.navIcon}>{icon}</span>
      <div style={styles.navText}>
        <div style={styles.navLabel}>{label}</div>
        <div style={styles.navSubtitle}>{subtitle}</div>
      </div>
      {active && <div style={styles.navIndicator} />}
    </button>
  )
}

// 概览页面
function OverviewTab({ stats, loading }) {
  return (
    <div style={styles.content}>
      {/* 页面标题 */}
      <div style={styles.pageHeader}>
        <div style={styles.pageNumber}>04</div>
        <h1 style={styles.pageTitle}>System Overview</h1>
        <p style={styles.pageSubtitle}>实时监控 · 数据统计 · 性能分析</p>
      </div>

      {/* 统计卡片网格 */}
      <div style={styles.statsGrid}>
        <StatCard
          title="Total Projects"
          subtitle="总项目数"
          value={stats.totalProjects}
          color="#D4A574"
          delay={0}
        />
        <StatCard
          title="Total Jobs"
          subtitle="总任务数"
          value={stats.totalJobs}
          color="#8B7355"
          delay={100}
        />
        <StatCard
          title="Running"
          subtitle="运行中"
          value={stats.runningJobs}
          color="#D4A574"
          delay={200}
          pulse={stats.runningJobs > 0}
        />
        <StatCard
          title="Completed"
          subtitle="已完成"
          value={stats.completedJobs}
          color="#2C2416"
          delay={300}
        />
        <StatCard
          title="Failed"
          subtitle="失败"
          value={stats.failedJobs}
          color="#C89564"
          delay={400}
        />
      </div>
    </div>
  )
}

// 统计卡片组件
function StatCard({ title, subtitle, value, color, delay, pulse }) {
  const [isHovered, setIsHovered] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setTimeout(() => setMounted(true), delay)
  }, [delay])

  return (
    <div
      style={{
        ...styles.statCard,
        opacity: mounted ? 1 : 0,
        transform: mounted
          ? isHovered ? 'translateY(-4px)' : 'translateY(0)'
          : 'translateY(20px)',
        borderColor: isHovered ? color : '#E8E6E0'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 内容 */}
      <div style={styles.statContent}>
        <div style={styles.statHeader}>
          <div style={styles.statTitle}>{title}</div>
          <div style={styles.statSubtitle}>{subtitle}</div>
        </div>
        <div style={{
          ...styles.statValue,
          color: color,
          animation: pulse ? 'pulse 2s ease-in-out infinite' : 'none'
        }}>
          {value}
        </div>
      </div>

      {/* 装饰线条 */}
      <div style={{
        ...styles.statDecorLine,
        backgroundColor: color,
        width: isHovered ? '100%' : '0%'
      }} />
    </div>
  )
}

// 其他标签页
function ProjectsTab() {
  return (
    <div style={styles.content}>
      <div style={styles.pageHeader}>
        <div style={styles.pageNumber}>04</div>
        <h1 style={styles.pageTitle}>Project Management</h1>
        <p style={styles.pageSubtitle}>项目管理 · 创建 · 编辑 · 删除</p>
      </div>
      <ProjectsManager />
    </div>
  )
}

function JobsTab() {
  return (
    <div style={styles.content}>
      <div style={styles.pageHeader}>
        <div style={styles.pageNumber}>04</div>
        <h1 style={styles.pageTitle}>Job Management</h1>
        <p style={styles.pageSubtitle}>任务管理 · 监控 · 控制</p>
      </div>
      <JobsManager />
    </div>
  )
}

function LogsTab() {
  return (
    <div style={styles.content}>
      <div style={styles.pageHeader}>
        <div style={styles.pageNumber}>04</div>
        <h1 style={styles.pageTitle}>System Logs</h1>
        <p style={styles.pageSubtitle}>系统日志 · 实时监控</p>
      </div>
      <LogsViewer />
    </div>
  )
}

function ResourcesTab() {
  return (
    <div style={styles.content}>
      <div style={styles.pageHeader}>
        <div style={styles.pageNumber}>04</div>
        <h1 style={styles.pageTitle}>Resource Manager</h1>
        <p style={styles.pageSubtitle}>资源管理 · 存储 · 优化</p>
      </div>
      <ResourcesManager />
    </div>
  )
}

// 样式定义
const styles = {
  // 容器
  container: {
    display: 'flex',
    minHeight: '100vh',
    backgroundColor: '#FAF9F6',
    position: 'relative',
    overflow: 'hidden'
  },

  // 侧边栏
  sidebar: {
    width: '280px',
    backgroundColor: '#FFFFFF',
    borderRight: '1px solid #E8E6E0',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    zIndex: 10,
    transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)'
  },

  // Logo 区域
  sidebarHeader: {
    padding: '40px 24px',
    borderBottom: '1px solid #E8E6E0'
  },
  logoContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  },
  logoIcon: {
    fontSize: '32px',
    lineHeight: 1
  },
  sidebarTitle: {
    margin: 0,
    fontSize: '24px',
    fontWeight: '300',
    fontFamily: 'Georgia, "Times New Roman", serif',
    color: '#2C2416',
    letterSpacing: '-0.01em'
  },
  sidebarSubtitle: {
    margin: '4px 0 0 0',
    fontSize: '11px',
    fontWeight: '500',
    color: '#8B7355',
    letterSpacing: '0.1em',
    textTransform: 'uppercase'
  },

  // 导航
  nav: {
    flex: 1,
    padding: '24px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  navItem: {
    width: '100%',
    padding: '16px 20px',
    border: '1px solid #E8E6E0',
    backgroundColor: 'transparent',
    color: '#2C2416',
    textAlign: 'left',
    cursor: 'pointer',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    position: 'relative',
    overflow: 'hidden'
  },
  navItemActive: {
    backgroundColor: '#FAF9F6',
    borderColor: '#D4A574',
    color: '#2C2416'
  },
  navIcon: {
    fontSize: '16px',
    lineHeight: 1,
    fontWeight: '600',
    fontFamily: 'Georgia, "Times New Roman", serif',
    color: '#D4A574',
    minWidth: '24px'
  },
  navText: {
    flex: 1
  },
  navLabel: {
    fontSize: '13px',
    fontWeight: '500',
    letterSpacing: '0.05em',
    marginBottom: '2px'
  },
  navSubtitle: {
    fontSize: '11px',
    color: '#8B7355',
    letterSpacing: '0.05em'
  },
  navIndicator: {
    position: 'absolute',
    right: 0,
    top: 0,
    bottom: 0,
    width: '3px',
    backgroundColor: '#D4A574'
  },

  // 底部
  sidebarFooter: {
    padding: '20px 16px',
    borderTop: '1px solid #E8E6E0'
  },
  backButton: {
    width: '100%',
    padding: '14px 20px',
    border: '1px solid #E8E6E0',
    backgroundColor: 'transparent',
    color: '#2C2416',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    letterSpacing: '0.05em',
    textTransform: 'uppercase'
  },
  backIcon: {
    fontSize: '16px'
  },

  // 主内容区
  main: {
    flex: 1,
    overflow: 'auto',
    position: 'relative',
    zIndex: 5,
    backgroundColor: '#FAF9F6'
  },
  mainContent: {
    transition: 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
    transitionDelay: '200ms'
  },

  // 内容区
  content: {
    padding: '60px 56px',
    maxWidth: '1400px',
    margin: '0 auto'
  },

  // 页面标题
  pageHeader: {
    marginBottom: '60px'
  },
  pageNumber: {
    fontSize: '120px',
    fontWeight: '300',
    color: '#E8E6E0',
    lineHeight: '1',
    marginBottom: '-30px',
    fontFamily: 'Georgia, "Times New Roman", serif',
    userSelect: 'none'
  },
  pageTitle: {
    margin: 0,
    fontSize: '48px',
    fontWeight: '300',
    fontFamily: 'Georgia, "Times New Roman", serif',
    color: '#2C2416',
    letterSpacing: '-0.02em',
    marginBottom: '12px'
  },
  pageSubtitle: {
    margin: 0,
    fontSize: '13px',
    color: '#8B7355',
    letterSpacing: '0.1em',
    fontWeight: '500'
  },

  // 统计网格
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '24px'
  },

  // 统计卡片
  statCard: {
    backgroundColor: '#FFFFFF',
    padding: '32px',
    border: '1px solid #E8E6E0',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    cursor: 'pointer',
    position: 'relative',
    overflow: 'hidden'
  },
  statContent: {
    position: 'relative',
    zIndex: 2
  },
  statHeader: {
    marginBottom: '20px'
  },
  statTitle: {
    fontSize: '12px',
    fontWeight: '500',
    color: '#2C2416',
    letterSpacing: '0.1em',
    marginBottom: '4px',
    textTransform: 'uppercase'
  },
  statSubtitle: {
    fontSize: '11px',
    color: '#8B7355',
    letterSpacing: '0.05em'
  },
  statValue: {
    fontSize: '56px',
    fontWeight: '300',
    fontFamily: 'Georgia, "Times New Roman", serif',
    lineHeight: 1,
    transition: 'color 0.3s'
  },
  statDecorLine: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    height: '3px',
    transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
  }
}

export default AdminDashboard
