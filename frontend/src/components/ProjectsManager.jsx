/**
 * Editorial Studio - Projects Manager
 * 项目管理组件 - Editorial Studio 美学
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { formatLocalTime } from '../utils/dateUtils'

const API_BASE = 'http://localhost:8000'

function ProjectsManager() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProject, setSelectedProject] = useState(null)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/projects`)
      setProjects(response.data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const viewProject = async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE}/projects/${projectId}`)
      setSelectedProject(response.data)
    } catch (error) {
      console.error('Failed to load project:', error)
      alert('加载项目详情失败')
    }
  }

  const deleteProject = async (projectId) => {
    if (!confirm('确定要删除这个项目吗？')) return

    try {
      await axios.delete(`${API_BASE}/projects/${projectId}`)
      alert('项目已删除')
      loadProjects()
    } catch (error) {
      console.error('Failed to delete project:', error)
      alert('删除项目失败')
    }
  }

  const filteredProjects = projects.filter(p =>
    p.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.title?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.loadingSpinner}></div>
        <div style={styles.loadingText}>加载中...</div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      {/* 搜索和操作栏 */}
      <div style={styles.toolbar}>
        <div style={styles.searchWrapper}>
          <input
            type="text"
            placeholder="搜索项目 ID 或标题..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={styles.searchInput}
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              style={styles.clearButton}
            >
              ✕
            </button>
          )}
        </div>
        <button onClick={loadProjects} style={styles.refreshButton}>
          刷新
        </button>
      </div>

      {/* 结果统计 */}
      {projects.length > 0 && (
        <div style={styles.resultStats}>
          <span style={styles.resultCount}>{filteredProjects.length}</span>
          <span style={styles.resultSeparator}>/</span>
          <span style={styles.resultTotal}>{projects.length}</span>
          <span style={styles.resultLabel}>项目</span>
        </div>
      )}

      {/* 项目列表 */}
      {filteredProjects.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyTitle}>
            {searchTerm ? '未找到匹配项目' : '暂无项目'}
          </div>
          <div style={styles.emptySubtitle}>
            {searchTerm ? '尝试使用其他关键词搜索' : '创建新项目后将在这里显示'}
          </div>
        </div>
      ) : (
        <div style={styles.projectsGrid}>
          {filteredProjects.map((project, index) => (
            <ProjectCard
              key={project.id}
              project={project}
              index={index}
              onView={viewProject}
              onDelete={deleteProject}
              navigate={navigate}
            />
          ))}
        </div>
      )}

      {/* 项目详情模态框 */}
      {selectedProject && (
        <ProjectDetailModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  )
}

// 项目卡片组件
function ProjectCard({ project, index, onView, onDelete, navigate }) {
  const [isHovered, setIsHovered] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setTimeout(() => setMounted(true), index * 50)
  }, [index])

  const getStatusConfig = (status) => {
    const configs = {
      completed: { label: 'Completed', color: '#2C2416' },
      running: { label: 'Running', color: '#D4A574' },
      failed: { label: 'Failed', color: '#C89564' },
      draft: { label: 'Draft', color: '#8B7355' }
    }
    return configs[status] || { label: status, color: '#8B7355' }
  }

  const statusConfig = getStatusConfig(project.status)

  return (
    <div
      style={{
        ...styles.projectCard,
        opacity: mounted ? 1 : 0,
        transform: mounted
          ? isHovered ? 'translateY(-4px)' : 'translateY(0)'
          : 'translateY(20px)',
        borderColor: isHovered ? statusConfig.color : '#E8E6E0'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 卡片头部 */}
      <div style={styles.cardHeader}>
        <div style={styles.cardId}>
          <span style={styles.cardIdLabel}>ID</span>
          <code style={styles.cardIdValue}>{project.id}</code>
        </div>
        <div style={{
          ...styles.statusBadge,
          backgroundColor: `${statusConfig.color}15`,
          color: statusConfig.color,
          borderColor: statusConfig.color
        }}>
          {statusConfig.label}
        </div>
      </div>

      {/* 项目标题 */}
      <h3 style={styles.cardTitle}>{project.title || '未命名项目'}</h3>

      {/* 时间信息 */}
      <div style={styles.cardMeta}>
        <span style={styles.metaLabel}>创建时间</span>
        <span style={styles.metaValue}>{formatLocalTime(project.created_at)}</span>
      </div>

      {/* 操作按钮 */}
      <div style={styles.cardActions}>
        <button
          onClick={() => navigate(`/result/${project.id}`)}
          style={styles.actionButtonPrimary}
        >
          查看结果
        </button>
        <button
          onClick={() => navigate(`/generate/${project.id}`)}
          style={styles.actionButton}
        >
          查看进度
        </button>
        <button
          onClick={() => onView(project.id)}
          style={styles.actionButton}
        >
          详情
        </button>
        <button
          onClick={() => onDelete(project.id)}
          style={styles.actionButtonDanger}
        >
          删除
        </button>
      </div>

      {/* 装饰线 */}
      <div style={{
        ...styles.cardDecorLine,
        backgroundColor: statusConfig.color,
        width: isHovered ? '100%' : '0%'
      }} />
    </div>
  )
}

// 项目详情模态框
function ProjectDetailModal({ project, onClose }) {
  const navigate = useNavigate()
  const [scenes, setScenes] = useState([])
  const [loadingScenes, setLoadingScenes] = useState(false)

  useEffect(() => {
    const loadScenes = async () => {
      try {
        setLoadingScenes(true)
        const response = await axios.get(`${API_BASE}/projects/${project.id}/scenes`)
        setScenes(response.data)
      } catch (error) {
        console.error('Failed to load scenes:', error)
      } finally {
        setLoadingScenes(false)
      }
    }

    loadScenes()

    // ESC 键关闭
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [project.id, onClose])

  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* 模态框头部 */}
        <div style={styles.modalHeader}>
          <div>
            <h2 style={styles.modalTitle}>Project Details</h2>
            <p style={styles.modalSubtitle}>项目详情</p>
          </div>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>

        {/* 模态框内容 */}
        <div style={styles.modalBody}>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>项目 ID</span>
            <code style={styles.detailValue}>{project.id}</code>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>标题</span>
            <span style={styles.detailValue}>{project.title || '-'}</span>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>状态</span>
            <span style={styles.detailValue}>{project.status}</span>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>创建时间</span>
            <span style={styles.detailValue}>{formatLocalTime(project.created_at)}</span>
          </div>

          {/* 场景列表 */}
          {loadingScenes ? (
            <div style={styles.scenesLoading}>加载场景中...</div>
          ) : scenes.length > 0 ? (
            <div style={styles.scenesSection}>
              <h3 style={styles.sectionTitle}>场景列表</h3>
              <div style={styles.scenesList}>
                {scenes.map((scene, index) => (
                  <div key={scene.scene_id} style={styles.sceneItem}>
                    <div style={styles.sceneInfo}>
                      <span style={styles.sceneNumber}>场景 {index + 1}</span>
                      <span style={styles.sceneType}>{scene.template_type}</span>
                    </div>
                    <button
                      onClick={() => navigate(`/timeline-editor/${scene.scene_id}`)}
                      style={styles.sceneButton}
                    >
                      编辑
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}

// 样式定义
const styles = {
  container: {
    padding: '0'
  },

  // 工具栏
  toolbar: {
    display: 'flex',
    gap: '16px',
    marginBottom: '24px',
    alignItems: 'center'
  },
  searchWrapper: {
    flex: 1,
    position: 'relative',
    display: 'flex',
    alignItems: 'center'
  },
  searchInput: {
    flex: 1,
    padding: '14px 40px 14px 16px',
    backgroundColor: '#FFFFFF',
    border: '1px solid #E8E6E0',
    fontSize: '14px',
    color: '#2C2416',
    outline: 'none',
    transition: 'all 0.3s',
    fontFamily: 'inherit'
  },
  clearButton: {
    position: 'absolute',
    right: '12px',
    width: '24px',
    height: '24px',
    border: 'none',
    borderRadius: '50%',
    background: '#E8E6E0',
    color: '#8B7355',
    cursor: 'pointer',
    fontSize: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.3s',
    padding: 0
  },
  refreshButton: {
    padding: '14px 28px',
    backgroundColor: '#2C2416',
    color: '#FFFFFF',
    border: 'none',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
    transition: 'all 0.3s',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    whiteSpace: 'nowrap'
  },

  // 结果统计
  resultStats: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '8px',
    marginBottom: '24px',
    fontSize: '13px',
    color: '#8B7355',
    fontWeight: '500'
  },
  resultCount: {
    fontSize: '32px',
    color: '#D4A574',
    fontWeight: '300',
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  resultSeparator: {
    color: '#E8E6E0'
  },
  resultTotal: {
    fontSize: '18px',
    color: '#8B7355'
  },
  resultLabel: {
    marginLeft: '4px',
    letterSpacing: '0.1em'
  },

  // Loading
  loading: {
    textAlign: 'center',
    padding: '80px 20px',
    color: '#8B7355'
  },
  loadingSpinner: {
    width: '40px',
    height: '40px',
    border: '3px solid #E8E6E0',
    borderTop: '3px solid #D4A574',
    borderRadius: '50%',
    margin: '0 auto 20px',
    animation: 'spin 1s linear infinite'
  },
  loadingText: {
    fontSize: '14px',
    letterSpacing: '0.05em'
  },

  // Empty 状态
  empty: {
    textAlign: 'center',
    padding: '100px 20px',
    backgroundColor: '#FFFFFF',
    border: '1px solid #E8E6E0'
  },
  emptyTitle: {
    fontSize: '18px',
    fontWeight: '300',
    color: '#2C2416',
    letterSpacing: '0.05em',
    marginBottom: '8px',
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  emptySubtitle: {
    fontSize: '13px',
    color: '#8B7355',
    letterSpacing: '0.05em'
  },

  // 项目网格
  projectsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '24px'
  },

  // 项目卡片
  projectCard: {
    backgroundColor: '#FFFFFF',
    padding: '28px',
    border: '1px solid #E8E6E0',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    cursor: 'pointer',
    position: 'relative',
    overflow: 'hidden'
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px'
  },
  cardId: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  cardIdLabel: {
    fontSize: '11px',
    color: '#8B7355',
    letterSpacing: '0.1em',
    fontWeight: '500',
    textTransform: 'uppercase'
  },
  cardIdValue: {
    fontSize: '12px',
    color: '#2C2416',
    backgroundColor: '#FAF9F6',
    padding: '4px 10px',
    fontFamily: 'inherit',
    letterSpacing: '0.05em'
  },
  statusBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '6px 12px',
    fontSize: '11px',
    fontWeight: '500',
    letterSpacing: '0.05em',
    border: '1px solid',
    textTransform: 'uppercase'
  },
  cardTitle: {
    margin: '0 0 16px 0',
    fontSize: '18px',
    fontWeight: '300',
    color: '#2C2416',
    letterSpacing: '-0.01em',
    lineHeight: 1.4,
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  cardMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    marginBottom: '20px',
    fontSize: '12px',
    color: '#8B7355'
  },
  metaLabel: {
    fontWeight: '500',
    fontSize: '11px',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },
  metaValue: {
    color: '#2C2416',
    fontSize: '13px'
  },
  cardActions: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap'
  },
  actionButtonPrimary: {
    padding: '10px 16px',
    backgroundColor: '#2C2416',
    color: '#FFFFFF',
    border: 'none',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '500',
    transition: 'all 0.3s',
    letterSpacing: '0.05em',
    textTransform: 'uppercase'
  },
  actionButton: {
    padding: '10px 16px',
    backgroundColor: 'transparent',
    color: '#2C2416',
    border: '1px solid #E8E6E0',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '500',
    transition: 'all 0.3s',
    letterSpacing: '0.05em',
    textTransform: 'uppercase'
  },
  actionButtonDanger: {
    padding: '10px 16px',
    backgroundColor: 'transparent',
    color: '#C89564',
    border: '1px solid #C89564',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '500',
    transition: 'all 0.3s',
    letterSpacing: '0.05em',
    textTransform: 'uppercase'
  },
  cardDecorLine: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    height: '3px',
    transition: 'width 0.4s cubic-bezier(0.4, 0, 0.2, 1)'
  },

  // 模态框
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(44, 36, 22, 0.8)',
    backdropFilter: 'blur(10px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '20px'
  },
  modal: {
    backgroundColor: '#FFFFFF',
    maxWidth: '700px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'auto',
    border: '1px solid #E8E6E0'
  },
  modalHeader: {
    padding: '32px',
    borderBottom: '1px solid #E8E6E0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start'
  },
  modalTitle: {
    margin: 0,
    fontSize: '24px',
    fontWeight: '300',
    color: '#2C2416',
    letterSpacing: '-0.01em',
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  modalSubtitle: {
    margin: '4px 0 0 0',
    fontSize: '12px',
    color: '#8B7355',
    letterSpacing: '0.05em'
  },
  closeButton: {
    width: '36px',
    height: '36px',
    backgroundColor: 'transparent',
    border: '1px solid #E8E6E0',
    color: '#8B7355',
    cursor: 'pointer',
    fontSize: '18px',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  modalBody: {
    padding: '32px'
  },
  detailRow: {
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  detailLabel: {
    fontSize: '11px',
    color: '#8B7355',
    fontWeight: '500',
    letterSpacing: '0.1em',
    textTransform: 'uppercase'
  },
  detailValue: {
    fontSize: '14px',
    color: '#2C2416',
    letterSpacing: '0.05em'
  },
  scenesSection: {
    marginTop: '32px',
    paddingTop: '32px',
    borderTop: '1px solid #E8E6E0'
  },
  sectionTitle: {
    margin: '0 0 20px 0',
    fontSize: '16px',
    fontWeight: '300',
    color: '#2C2416',
    letterSpacing: '-0.01em',
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  scenesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  sceneItem: {
    padding: '16px',
    backgroundColor: '#FAF9F6',
    border: '1px solid #E8E6E0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  sceneInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  sceneNumber: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#2C2416',
    letterSpacing: '0.05em'
  },
  sceneType: {
    fontSize: '11px',
    color: '#8B7355',
    letterSpacing: '0.05em'
  },
  sceneButton: {
    padding: '10px 20px',
    backgroundColor: '#2C2416',
    color: '#FFFFFF',
    border: 'none',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '500',
    transition: 'all 0.3s',
    letterSpacing: '0.05em',
    textTransform: 'uppercase'
  },
  scenesLoading: {
    textAlign: 'center',
    padding: '40px',
    color: '#8B7355',
    fontSize: '13px',
    letterSpacing: '0.05em'
  }
}

export default ProjectsManager
