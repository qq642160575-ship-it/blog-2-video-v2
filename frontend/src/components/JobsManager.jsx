/**
 * input: 依赖 React 和后端任务 API。
 * output: 向外提供任务列表管理和监控功能。
 * pos: 位于组件层，负责任务的查询、重试和日志查看。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function JobsManager() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, running, completed, failed
  const [selectedJob, setSelectedJob] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(false)

  useEffect(() => {
    loadJobs()
  }, [])

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      loadJobs()
    }, 3000)

    return () => clearInterval(interval)
  }, [autoRefresh])

  const loadJobs = async () => {
    try {
      setLoading(true)
      // 注意：需要后端添加获取所有任务的 API
      // 暂时使用空数组
      setJobs([])
    } catch (error) {
      console.error('Failed to load jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const viewJobDetail = async (jobId) => {
    try {
      const response = await axios.get(`${API_BASE}/jobs/${jobId}`)
      setSelectedJob(response.data)
    } catch (error) {
      console.error('Failed to load job:', error)
      alert('加载任务详情失败')
    }
  }

  const retryJob = async (jobId) => {
    if (!confirm('确定要重试这个任务吗？')) return

    try {
      // 需要后端添加重试 API
      alert('重试功能开发中')
    } catch (error) {
      console.error('Failed to retry job:', error)
      alert('重试任务失败')
    }
  }

  const cancelJob = async (jobId) => {
    if (!confirm('确定要取消这个任务吗？')) return

    try {
      await axios.post(`${API_BASE}/jobs/${jobId}/cancel`)
      alert('任务已取消')
      loadJobs()
    } catch (error) {
      console.error('Failed to cancel job:', error)
      alert('取消任务失败')
    }
  }

  const filteredJobs = jobs.filter(job => {
    if (filter === 'all') return true
    return job.status === filter
  })

  if (loading && jobs.length === 0) {
    return <div style={styles.loading}>加载中...</div>
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.filters}>
          <button
            style={{...styles.filterButton, ...(filter === 'all' ? styles.filterActive : {})}}
            onClick={() => setFilter('all')}
          >
            全部 ({jobs.length})
          </button>
          <button
            style={{...styles.filterButton, ...(filter === 'running' ? styles.filterActive : {})}}
            onClick={() => setFilter('running')}
          >
            运行中 ({jobs.filter(j => j.status === 'running').length})
          </button>
          <button
            style={{...styles.filterButton, ...(filter === 'completed' ? styles.filterActive : {})}}
            onClick={() => setFilter('completed')}
          >
            已完成 ({jobs.filter(j => j.status === 'completed').length})
          </button>
          <button
            style={{...styles.filterButton, ...(filter === 'failed' ? styles.filterActive : {})}}
            onClick={() => setFilter('failed')}
          >
            失败 ({jobs.filter(j => j.status === 'failed').length})
          </button>
        </div>
        <div style={styles.actions}>
          <label style={styles.autoRefreshLabel}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span style={styles.autoRefreshText}>自动刷新</span>
          </label>
          <button onClick={loadJobs} style={styles.refreshButton}>
            🔄 刷新
          </button>
        </div>
      </div>

      {filteredJobs.length === 0 ? (
        <div style={styles.empty}>
          <p>暂无{filter !== 'all' ? getFilterName(filter) : ''}任务数据</p>
        </div>
      ) : (
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>任务 ID</th>
                <th style={styles.th}>项目 ID</th>
                <th style={styles.th}>类型</th>
                <th style={styles.th}>状态</th>
                <th style={styles.th}>阶段</th>
                <th style={styles.th}>进度</th>
                <th style={styles.th}>创建时间</th>
                <th style={styles.th}>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredJobs.map(job => (
                <tr key={job.id} style={styles.tr}>
                  <td style={styles.td}>
                    <code style={styles.code}>{job.id}</code>
                  </td>
                  <td style={styles.td}>
                    <code style={styles.code}>{job.project_id}</code>
                  </td>
                  <td style={styles.td}>{job.job_type}</td>
                  <td style={styles.td}>
                    <span style={getStatusStyle(job.status)}>
                      {getStatusText(job.status)}
                    </span>
                  </td>
                  <td style={styles.td}>{job.stage || '-'}</td>
                  <td style={styles.td}>
                    <ProgressBar progress={job.progress || 0} />
                  </td>
                  <td style={styles.td}>
                    {new Date(job.created_at).toLocaleString('zh-CN')}
                  </td>
                  <td style={styles.td}>
                    <button
                      onClick={() => viewJobDetail(job.id)}
                      style={styles.actionButton}
                    >
                      详情
                    </button>
                    {job.status === 'failed' && (
                      <button
                        onClick={() => retryJob(job.id)}
                        style={{...styles.actionButton, ...styles.retryButton}}
                      >
                        重试
                      </button>
                    )}
                    {job.status === 'running' && (
                      <button
                        onClick={() => cancelJob(job.id)}
                        style={{...styles.actionButton, ...styles.cancelButton}}
                      >
                        取消
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedJob && (
        <JobDetailModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </div>
  )
}

function ProgressBar({ progress }) {
  const percentage = Math.round(progress * 100)
  return (
    <div style={styles.progressContainer}>
      <div style={{...styles.progressBar, width: `${percentage}%`}} />
      <span style={styles.progressText}>{percentage}%</span>
    </div>
  )
}

function JobDetailModal({ job, onClose }) {
  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>任务详情</h2>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>
        <div style={styles.modalBody}>
          <div style={styles.detailRow}>
            <strong>任务 ID:</strong>
            <code style={styles.code}>{job.id}</code>
          </div>
          <div style={styles.detailRow}>
            <strong>项目 ID:</strong>
            <code style={styles.code}>{job.project_id}</code>
          </div>
          <div style={styles.detailRow}>
            <strong>类型:</strong>
            <span>{job.job_type}</span>
          </div>
          <div style={styles.detailRow}>
            <strong>状态:</strong>
            <span style={getStatusStyle(job.status)}>{getStatusText(job.status)}</span>
          </div>
          <div style={styles.detailRow}>
            <strong>阶段:</strong>
            <span>{job.stage || '-'}</span>
          </div>
          <div style={styles.detailRow}>
            <strong>进度:</strong>
            <ProgressBar progress={job.progress || 0} />
          </div>
          <div style={styles.detailRow}>
            <strong>创建时间:</strong>
            <span>{new Date(job.created_at).toLocaleString('zh-CN')}</span>
          </div>
          {job.error_message && (
            <div style={styles.detailRow}>
              <strong>错误信息:</strong>
              <pre style={styles.errorPre}>{job.error_message}</pre>
            </div>
          )}
          {job.result_data && (
            <div style={styles.detailRow}>
              <strong>结果数据:</strong>
              <pre style={styles.pre}>{JSON.stringify(job.result_data, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function getFilterName(filter) {
  const names = {
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return names[filter] || ''
}

function getStatusText(status) {
  const texts = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return texts[status] || status
}

function getStatusStyle(status) {
  const baseStyle = {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600',
    display: 'inline-block'
  }

  switch (status) {
    case 'completed':
      return { ...baseStyle, backgroundColor: '#d1fae5', color: '#065f46' }
    case 'running':
      return { ...baseStyle, backgroundColor: '#fef3c7', color: '#92400e' }
    case 'failed':
      return { ...baseStyle, backgroundColor: '#fee2e2', color: '#991b1b' }
    case 'cancelled':
      return { ...baseStyle, backgroundColor: '#e5e7eb', color: '#374151' }
    default:
      return { ...baseStyle, backgroundColor: '#dbeafe', color: '#1e40af' }
  }
}

const styles = {
  container: {
    padding: '20px'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    flexWrap: 'wrap',
    gap: '12px'
  },
  filters: {
    display: 'flex',
    gap: '8px'
  },
  filterButton: {
    padding: '8px 16px',
    backgroundColor: 'white',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151'
  },
  filterActive: {
    backgroundColor: '#667eea',
    color: 'white',
    borderColor: '#667eea'
  },
  actions: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  },
  autoRefreshLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer'
  },
  autoRefreshText: {
    fontSize: '14px',
    color: '#374151'
  },
  refreshButton: {
    padding: '8px 16px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600'
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    color: '#6b7280'
  },
  empty: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#6b7280',
    backgroundColor: 'white',
    borderRadius: '12px'
  },
  tableContainer: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    overflow: 'auto'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    minWidth: '900px'
  },
  th: {
    padding: '16px',
    textAlign: 'left',
    backgroundColor: '#f9fafb',
    borderBottom: '2px solid #e5e7eb',
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
    whiteSpace: 'nowrap'
  },
  tr: {
    borderBottom: '1px solid #e5e7eb'
  },
  td: {
    padding: '16px',
    fontSize: '14px',
    color: '#1f2937'
  },
  code: {
    backgroundColor: '#f3f4f6',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '12px',
    fontFamily: 'monospace'
  },
  progressContainer: {
    position: 'relative',
    width: '100px',
    height: '20px',
    backgroundColor: '#e5e7eb',
    borderRadius: '10px',
    overflow: 'hidden'
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#667eea',
    transition: 'width 0.3s'
  },
  progressText: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    fontSize: '11px',
    fontWeight: '600',
    color: '#1f2937'
  },
  actionButton: {
    padding: '6px 12px',
    marginRight: '8px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '600'
  },
  retryButton: {
    backgroundColor: '#f59e0b'
  },
  cancelButton: {
    backgroundColor: '#ef4444'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '12px',
    maxWidth: '700px',
    width: '90%',
    maxHeight: '80vh',
    overflow: 'auto',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
  },
  modalHeader: {
    padding: '20px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  modalTitle: {
    margin: 0,
    fontSize: '20px',
    fontWeight: 'bold'
  },
  closeButton: {
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer',
    color: '#6b7280'
  },
  modalBody: {
    padding: '20px'
  },
  detailRow: {
    marginBottom: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px'
  },
  pre: {
    backgroundColor: '#f3f4f6',
    padding: '12px',
    borderRadius: '6px',
    fontSize: '12px',
    overflow: 'auto',
    maxHeight: '200px'
  },
  errorPre: {
    backgroundColor: '#fee2e2',
    padding: '12px',
    borderRadius: '6px',
    fontSize: '12px',
    overflow: 'auto',
    maxHeight: '200px',
    color: '#991b1b'
  }
}

export default JobsManager
