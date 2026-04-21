/**
 * input: 依赖 React 和后端日志 API。
 * output: 向外提供 AI 日志和任务日志查看功能。
 * pos: 位于组件层，负责日志的查询、过滤和详情展示。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function LogsViewer() {
  const [logType, setLogType] = useState('ai') // ai, job
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    jobId: '',
    projectId: '',
    operation: '',
    limit: 100
  })
  const [selectedLog, setSelectedLog] = useState(null)

  useEffect(() => {
    loadLogs()
  }, [logType, filters])

  const loadLogs = async () => {
    try {
      setLoading(true)
      if (logType === 'ai') {
        const params = new URLSearchParams()
        if (filters.jobId) params.append('job_id', filters.jobId)
        if (filters.projectId) params.append('project_id', filters.projectId)
        if (filters.operation) params.append('operation', filters.operation)
        params.append('limit', filters.limit.toString())

        const response = await axios.get(`${API_BASE}/logs/ai?${params}`)
        setLogs(response.data)
      } else {
        const params = new URLSearchParams()
        if (filters.jobId) params.append('job_id', filters.jobId)
        params.append('limit', filters.limit.toString())

        const response = await axios.get(`${API_BASE}/logs/job?${params}`)
        setLogs(response.data)
      }
    } catch (error) {
      console.error('Failed to load logs:', error)
      setLogs([])
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    setFilters({
      jobId: '',
      projectId: '',
      operation: '',
      limit: 100
    })
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.tabs}>
          <button
            style={{...styles.tab, ...(logType === 'ai' ? styles.tabActive : {})}}
            onClick={() => setLogType('ai')}
          >
            AI 日志
          </button>
          <button
            style={{...styles.tab, ...(logType === 'job' ? styles.tabActive : {})}}
            onClick={() => setLogType('job')}
          >
            任务日志
          </button>
        </div>
      </div>

      <div style={styles.filters}>
        <input
          type="text"
          placeholder="任务 ID"
          value={filters.jobId}
          onChange={(e) => handleFilterChange('jobId', e.target.value)}
          style={styles.filterInput}
        />
        {logType === 'ai' && (
          <>
            <input
              type="text"
              placeholder="项目 ID"
              value={filters.projectId}
              onChange={(e) => handleFilterChange('projectId', e.target.value)}
              style={styles.filterInput}
            />
            <input
              type="text"
              placeholder="操作类型"
              value={filters.operation}
              onChange={(e) => handleFilterChange('operation', e.target.value)}
              style={styles.filterInput}
            />
          </>
        )}
        <select
          value={filters.limit}
          onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
          style={styles.filterSelect}
        >
          <option value={50}>50 条</option>
          <option value={100}>100 条</option>
          <option value={200}>200 条</option>
          <option value={500}>500 条</option>
        </select>
        <button onClick={clearFilters} style={styles.clearButton}>
          清除筛选
        </button>
        <button onClick={loadLogs} style={styles.refreshButton}>
          🔄 刷新
        </button>
      </div>

      {loading ? (
        <div style={styles.loading}>加载中...</div>
      ) : logs.length === 0 ? (
        <div style={styles.empty}>暂无日志数据</div>
      ) : (
        <div style={styles.logsContainer}>
          {logType === 'ai' ? (
            <AILogsList logs={logs} onSelect={setSelectedLog} />
          ) : (
            <JobLogsList logs={logs} onSelect={setSelectedLog} />
          )}
        </div>
      )}

      {selectedLog && (
        <LogDetailModal
          log={selectedLog}
          type={logType}
          onClose={() => setSelectedLog(null)}
        />
      )}
    </div>
  )
}

function AILogsList({ logs, onSelect }) {
  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>时间</th>
            <th style={styles.th}>操作</th>
            <th style={styles.th}>模型</th>
            <th style={styles.th}>Token</th>
            <th style={styles.th}>耗时</th>
            <th style={styles.th}>成本</th>
            <th style={styles.th}>状态</th>
            <th style={styles.th}>操作</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr key={log.id} style={styles.tr}>
              <td style={styles.td}>
                {new Date(log.created_at).toLocaleString('zh-CN')}
              </td>
              <td style={styles.td}>{log.operation}</td>
              <td style={styles.td}>
                <code style={styles.code}>{log.model}</code>
              </td>
              <td style={styles.td}>
                {log.tokens_input && log.tokens_output
                  ? `${log.tokens_input} / ${log.tokens_output}`
                  : '-'}
              </td>
              <td style={styles.td}>
                {log.duration_ms ? `${log.duration_ms}ms` : '-'}
              </td>
              <td style={styles.td}>
                {log.cost ? `¥${log.cost.toFixed(4)}` : '-'}
              </td>
              <td style={styles.td}>
                <span style={getLogStatusStyle(log.status)}>
                  {log.status}
                </span>
              </td>
              <td style={styles.td}>
                <button
                  onClick={() => onSelect(log)}
                  style={styles.viewButton}
                >
                  查看
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function JobLogsList({ logs, onSelect }) {
  return (
    <div style={styles.tableContainer}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>时间</th>
            <th style={styles.th}>任务 ID</th>
            <th style={styles.th}>级别</th>
            <th style={styles.th}>消息</th>
            <th style={styles.th}>操作</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr key={log.id} style={styles.tr}>
              <td style={styles.td}>
                {new Date(log.created_at).toLocaleString('zh-CN')}
              </td>
              <td style={styles.td}>
                <code style={styles.code}>{log.job_id}</code>
              </td>
              <td style={styles.td}>
                <span style={getLogLevelStyle(log.level)}>
                  {log.level}
                </span>
              </td>
              <td style={styles.td}>
                <div style={styles.messagePreview}>
                  {log.message.substring(0, 100)}
                  {log.message.length > 100 && '...'}
                </div>
              </td>
              <td style={styles.td}>
                <button
                  onClick={() => onSelect(log)}
                  style={styles.viewButton}
                >
                  查看
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function LogDetailModal({ log, type, onClose }) {
  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>日志详情</h2>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>
        <div style={styles.modalBody}>
          {type === 'ai' ? (
            <>
              <div style={styles.detailRow}>
                <strong>操作:</strong>
                <span>{log.operation}</span>
              </div>
              <div style={styles.detailRow}>
                <strong>模型:</strong>
                <code style={styles.code}>{log.model}</code>
              </div>
              <div style={styles.detailRow}>
                <strong>Prompt:</strong>
                <pre style={styles.pre}>{log.prompt}</pre>
              </div>
              <div style={styles.detailRow}>
                <strong>Response:</strong>
                <pre style={styles.pre}>{log.response}</pre>
              </div>
              <div style={styles.detailRow}>
                <strong>Token 使用:</strong>
                <span>输入: {log.tokens_input || 0} / 输出: {log.tokens_output || 0}</span>
              </div>
              <div style={styles.detailRow}>
                <strong>耗时:</strong>
                <span>{log.duration_ms}ms</span>
              </div>
              <div style={styles.detailRow}>
                <strong>成本:</strong>
                <span>¥{log.cost?.toFixed(4) || '0.0000'}</span>
              </div>
              {log.error_message && (
                <div style={styles.detailRow}>
                  <strong>错误信息:</strong>
                  <pre style={styles.errorPre}>{log.error_message}</pre>
                </div>
              )}
            </>
          ) : (
            <>
              <div style={styles.detailRow}>
                <strong>任务 ID:</strong>
                <code style={styles.code}>{log.job_id}</code>
              </div>
              <div style={styles.detailRow}>
                <strong>级别:</strong>
                <span style={getLogLevelStyle(log.level)}>{log.level}</span>
              </div>
              <div style={styles.detailRow}>
                <strong>消息:</strong>
                <pre style={styles.pre}>{log.message}</pre>
              </div>
              <div style={styles.detailRow}>
                <strong>时间:</strong>
                <span>{new Date(log.created_at).toLocaleString('zh-CN')}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function getLogStatusStyle(status) {
  const baseStyle = {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600'
  }

  switch (status) {
    case 'success':
      return { ...baseStyle, backgroundColor: '#d1fae5', color: '#065f46' }
    case 'error':
      return { ...baseStyle, backgroundColor: '#fee2e2', color: '#991b1b' }
    default:
      return { ...baseStyle, backgroundColor: '#e5e7eb', color: '#374151' }
  }
}

function getLogLevelStyle(level) {
  const baseStyle = {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600'
  }

  switch (level) {
    case 'ERROR':
      return { ...baseStyle, backgroundColor: '#fee2e2', color: '#991b1b' }
    case 'WARNING':
      return { ...baseStyle, backgroundColor: '#fef3c7', color: '#92400e' }
    case 'INFO':
      return { ...baseStyle, backgroundColor: '#dbeafe', color: '#1e40af' }
    default:
      return { ...baseStyle, backgroundColor: '#e5e7eb', color: '#374151' }
  }
}

const styles = {
  container: {
    padding: '20px'
  },
  header: {
    marginBottom: '20px'
  },
  tabs: {
    display: 'flex',
    gap: '8px',
    borderBottom: '2px solid #e5e7eb'
  },
  tab: {
    padding: '12px 24px',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    cursor: 'pointer',
    fontSize: '15px',
    fontWeight: '500',
    color: '#6b7280',
    marginBottom: '-2px'
  },
  tabActive: {
    color: '#667eea',
    borderBottomColor: '#667eea'
  },
  filters: {
    display: 'flex',
    gap: '12px',
    marginBottom: '20px',
    flexWrap: 'wrap'
  },
  filterInput: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    minWidth: '150px'
  },
  filterSelect: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer'
  },
  clearButton: {
    padding: '8px 16px',
    backgroundColor: '#6b7280',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600'
  },
  refreshButton: {
    padding: '8px 16px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
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
  logsContainer: {
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  tableContainer: {
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
  messagePreview: {
    maxWidth: '400px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap'
  },
  viewButton: {
    padding: '6px 12px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '600'
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
    maxWidth: '800px',
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
    alignItems: 'center',
    position: 'sticky',
    top: 0,
    backgroundColor: 'white',
    zIndex: 1
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
    maxHeight: '300px',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word'
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

export default LogsViewer
