/**
 * input: 依赖 React 和后端项目 API。
 * output: 向外提供项目列表管理功能。
 * pos: 位于组件层，负责项目的查询、删除和详情查看。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function ProjectsManager() {
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
      // 注意：需要后端添加获取所有项目的 API
      // 暂时使用空数组
      setProjects([])
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
    return <div style={styles.loading}>加载中...</div>
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <input
          type="text"
          placeholder="搜索项目 ID 或标题..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={styles.searchInput}
        />
        <button onClick={loadProjects} style={styles.refreshButton}>
          🔄 刷新
        </button>
      </div>

      {filteredProjects.length === 0 ? (
        <div style={styles.empty}>
          <p>暂无项目数据</p>
          <p style={styles.emptyHint}>创建新项目后将在这里显示</p>
        </div>
      ) : (
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>项目 ID</th>
                <th style={styles.th}>标题</th>
                <th style={styles.th}>状态</th>
                <th style={styles.th}>创建时间</th>
                <th style={styles.th}>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredProjects.map(project => (
                <tr key={project.id} style={styles.tr}>
                  <td style={styles.td}>
                    <code style={styles.code}>{project.id}</code>
                  </td>
                  <td style={styles.td}>{project.title || '-'}</td>
                  <td style={styles.td}>
                    <span style={getStatusStyle(project.status)}>
                      {project.status}
                    </span>
                  </td>
                  <td style={styles.td}>
                    {new Date(project.created_at).toLocaleString('zh-CN')}
                  </td>
                  <td style={styles.td}>
                    <button
                      onClick={() => viewProject(project.id)}
                      style={styles.actionButton}
                    >
                      查看
                    </button>
                    <button
                      onClick={() => deleteProject(project.id)}
                      style={{...styles.actionButton, ...styles.deleteButton}}
                    >
                      删除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedProject && (
        <ProjectDetailModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  )
}

function ProjectDetailModal({ project, onClose }) {
  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>项目详情</h2>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>
        <div style={styles.modalBody}>
          <div style={styles.detailRow}>
            <strong>项目 ID:</strong>
            <code style={styles.code}>{project.id}</code>
          </div>
          <div style={styles.detailRow}>
            <strong>标题:</strong>
            <span>{project.title || '-'}</span>
          </div>
          <div style={styles.detailRow}>
            <strong>状态:</strong>
            <span style={getStatusStyle(project.status)}>{project.status}</span>
          </div>
          <div style={styles.detailRow}>
            <strong>创建时间:</strong>
            <span>{new Date(project.created_at).toLocaleString('zh-CN')}</span>
          </div>
          {project.article_content && (
            <div style={styles.detailRow}>
              <strong>文章内容:</strong>
              <pre style={styles.pre}>{project.article_content}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function getStatusStyle(status) {
  const baseStyle = {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600'
  }

  switch (status) {
    case 'completed':
      return { ...baseStyle, backgroundColor: '#d1fae5', color: '#065f46' }
    case 'running':
      return { ...baseStyle, backgroundColor: '#fef3c7', color: '#92400e' }
    case 'failed':
      return { ...baseStyle, backgroundColor: '#fee2e2', color: '#991b1b' }
    default:
      return { ...baseStyle, backgroundColor: '#e5e7eb', color: '#374151' }
  }
}

const styles = {
  container: {
    padding: '20px'
  },
  header: {
    display: 'flex',
    gap: '12px',
    marginBottom: '20px'
  },
  searchInput: {
    flex: 1,
    padding: '10px 16px',
    border: '1px solid #f0eee6', // Border Cream
    borderRadius: '12px', // Generous
    fontSize: '14px',
    backgroundColor: '#ffffff',
    color: '#141413', // Near Black
    outline: 'none',
    transition: 'all 0.2s'
  },
  refreshButton: {
    padding: '10px 20px',
    backgroundColor: '#c96442', // Terracotta Brand
    color: '#faf9f5', // Ivory
    border: 'none',
    borderRadius: '8px', // Comfortable
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    boxShadow: '0px 0px 0px 1px #c96442', // Ring shadow
    transition: 'all 0.2s'
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    color: '#5e5d59', // Olive Gray
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  empty: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#5e5d59' // Olive Gray
  },
  emptyHint: {
    fontSize: '14px',
    marginTop: '8px',
    color: '#87867f' // Stone Gray
  },
  tableContainer: {
    backgroundColor: '#faf9f5', // Ivory
    borderRadius: '12px', // Generous
    border: '1px solid #f0eee6', // Border Cream
    boxShadow: 'rgba(0, 0, 0, 0.05) 0px 4px 24px', // Whisper shadow
    overflow: 'hidden'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse'
  },
  th: {
    padding: '16px',
    textAlign: 'left',
    backgroundColor: '#e8e6dc', // Warm Sand
    borderBottom: '1px solid #f0eee6', // Border Cream
    fontSize: '14px',
    fontWeight: '500',
    color: '#141413', // Near Black
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  tr: {
    borderBottom: '1px solid #f0eee6' // Border Cream
  },
  td: {
    padding: '16px',
    fontSize: '14px',
    color: '#141413', // Near Black
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  code: {
    backgroundColor: '#e8e6dc', // Warm Sand
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: 'monospace',
    color: '#4d4c48' // Charcoal Warm
  },
  actionButton: {
    padding: '6px 12px',
    marginRight: '8px',
    backgroundColor: '#e8e6dc', // Warm Sand
    color: '#4d4c48', // Charcoal Warm
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '500',
    transition: 'all 0.2s',
    boxShadow: '0px 0px 0px 1px #d1cfc5' // Ring shadow
  },
  deleteButton: {
    backgroundColor: '#b53333', // Error Crimson
    color: '#faf9f5', // Ivory
    boxShadow: '0px 0px 0px 1px #b53333'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(20, 20, 19, 0.5)', // Near Black with transparency
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  modal: {
    backgroundColor: '#faf9f5', // Ivory
    borderRadius: '16px', // Very rounded
    maxWidth: '600px',
    width: '90%',
    maxHeight: '80vh',
    overflow: 'auto',
    boxShadow: 'rgba(0, 0, 0, 0.15) 0px 20px 60px',
    border: '1px solid #f0eee6' // Border Cream
  },
  modalHeader: {
    padding: '20px',
    borderBottom: '1px solid #f0eee6', // Border Cream
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  modalTitle: {
    margin: 0,
    fontSize: '20.8px', // Feature Title
    fontWeight: '500',
    fontFamily: 'Georgia, serif', // Anthropic Serif fallback
    color: '#141413' // Near Black
  },
  closeButton: {
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer',
    color: '#87867f' // Stone Gray
  },
  modalBody: {
    padding: '20px'
  },
  detailRow: {
    marginBottom: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  pre: {
    backgroundColor: '#e8e6dc', // Warm Sand
    padding: '12px',
    borderRadius: '8px', // Comfortable
    fontSize: '12px',
    overflow: 'auto',
    maxHeight: '200px',
    fontFamily: 'monospace',
    color: '#4d4c48' // Charcoal Warm
  }
}

export default ProjectsManager
