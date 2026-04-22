/**
 * Cinema Studio Edition - Jobs Manager
 * Film production aesthetic with neon accents and dark theme
 */

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { formatLocalTime } from '../utils/dateUtils'

const API_BASE = 'http://localhost:8000'

function JobsManager_Cinema() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [selectedJob, setSelectedJob] = useState(null)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    loadJobs()
    setTimeout(() => setMounted(true), 50)
  }, [])

  useEffect(() => {
    if (!autoRefresh) return
    const interval = setInterval(() => loadJobs(), 3000)
    return () => clearInterval(interval)
  }, [autoRefresh])

  const loadJobs = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/jobs`)
      setJobs(response.data)
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
    return <div style={styles.loading}>⚙️ LOADING JOBS...</div>
  }

  const statusCounts = {
    all: jobs.length,
    running: jobs.filter(j => j.status === 'running').length,
    completed: jobs.filter(j => j.status === 'completed').length,
    failed: jobs.filter(j => j.status === 'failed').length
  }

  return (
    <div style={styles.container}>
      {/* Film strip decoration */}
      <div style={styles.filmStripLeft} />
      <div style={styles.filmStripRight} />

      {/* Header with filters */}
      <div style={styles.header}>
        <div style={styles.filters}>
          {['all', 'running', 'completed', 'failed'].map((f, idx) => (
            <FilterButton
              key={f}
              filter={f}
              active={filter === f}
              count={statusCounts[f]}
              onClick={() => setFilter(f)}
              delay={idx * 50}
              mounted={mounted}
            />
          ))}
        </div>

        <div style={styles.actions}>
          <label style={styles.autoRefreshLabel}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={styles.checkbox}
            />
            <span style={styles.autoRefreshText}>AUTO REFRESH</span>
          </label>
          <button onClick={loadJobs} style={styles.refreshButton}>
            🔄 REFRESH
          </button>
        </div>
      </div>

      {/* Jobs grid */}
      {filteredJobs.length === 0 ? (
        <div style={styles.empty}>
          <div style={styles.emptyIcon}>🎬</div>
          <div style={styles.emptyTitle}>NO JOBS FOUND</div>
          <div style={styles.emptyText}>
            {filter !== 'all' ? `No ${getFilterName(filter)} jobs` : 'No jobs yet'}
          </div>
        </div>
      ) : (
        <div style={styles.jobsGrid}>
          {filteredJobs.map((job, index) => (
            <JobCard
              key={job.id}
              job={job}
              index={index}
              mounted={mounted}
              onViewDetail={viewJobDetail}
              onRetry={retryJob}
              onCancel={cancelJob}
              navigate={navigate}
            />
          ))}
        </div>
      )}

      {selectedJob && (
        <JobDetailModal
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
          navigate={navigate}
        />
      )}
    </div>
  )
}

// Filter Button Component
function FilterButton({ filter, active, count, onClick, delay, mounted }) {
  const [isHovered, setIsHovered] = useState(false)

  const labels = {
    all: 'ALL JOBS',
    running: 'RUNNING',
    completed: 'COMPLETED',
    failed: 'FAILED'
  }

  const colors = {
    all: '#4ECDC4',
    running: '#FFE66D',
    completed: '#95E1D3',
    failed: '#FF6B6B'
  }

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        ...styles.filterButton,
        ...(active ? {
          background: `linear-gradient(135deg, ${colors[filter]} 0%, ${colors[filter]}dd 100%)`,
          color: '#0F0F0F',
          boxShadow: `0 0 20px ${colors[filter]}66`,
          transform: 'translateY(-2px)'
        } : {}),
        ...(isHovered && !active ? {
          borderColor: colors[filter],
          color: colors[filter],
          transform: 'translateY(-1px)'
        } : {}),
        opacity: mounted ? 1 : 0,
        transform: mounted ? (active ? 'translateY(-2px)' : 'translateY(0)') : 'translateY(10px)',
        transitionDelay: `${delay}ms`
      }}
    >
      <span style={styles.filterLabel}>{labels[filter]}</span>
      <span style={{
        ...styles.filterCount,
        color: active ? '#0F0F0F' : colors[filter]
      }}>{count}</span>
    </button>
  )
}

// Job Card Component
function JobCard({ job, index, mounted, onViewDetail, onRetry, onCancel, navigate }) {
  const [isHovered, setIsHovered] = useState(false)

  const statusConfig = {
    completed: { icon: '✓', label: 'COMPLETED', color: '#95E1D3', bg: '#95E1D322' },
    running: { icon: '⟳', label: 'RUNNING', color: '#FFE66D', bg: '#FFE66D22' },
    failed: { icon: '✕', label: 'FAILED', color: '#FF6B6B', bg: '#FF6B6B22' },
    cancelled: { icon: '○', label: 'CANCELLED', color: '#888', bg: '#88888822' },
    pending: { icon: '◷', label: 'PENDING', color: '#4ECDC4', bg: '#4ECDC422' }
  }

  const config = statusConfig[job.status] || statusConfig.pending

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        ...styles.jobCard,
        opacity: mounted ? 1 : 0,
        transform: mounted ? (isHovered ? 'translateY(-4px)' : 'translateY(0)') : 'translateY(20px)',
        transitionDelay: `${index * 50}ms`,
        boxShadow: isHovered ? `0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px ${config.color}33` : '0 4px 16px rgba(0, 0, 0, 0.3)'
      }}
    >
      {/* Status badge */}
      <div style={{
        ...styles.statusBadge,
        backgroundColor: config.bg,
        borderColor: config.color
      }}>
        <span style={{ fontSize: '14px' }}>{config.icon}</span>
        <span style={{ ...styles.statusText, color: config.color }}>{config.label}</span>
      </div>

      {/* Job info */}
      <div style={styles.jobInfo}>
        <div style={styles.jobId}>
          <span style={styles.jobIdLabel}>JOB</span>
          <code style={styles.code}>{job.id.slice(0, 8)}</code>
        </div>
        <div style={styles.jobMeta}>
          <span style={styles.metaItem}>📦 {job.job_type}</span>
          {job.stage && <span style={styles.metaItem}>🎬 {job.stage}</span>}
        </div>
        <div style={styles.jobTime}>{formatLocalTime(job.created_at)}</div>
      </div>

      {/* Progress bar */}
      <ProgressBar progress={job.progress || 0} status={job.status} />

      {/* Actions */}
      <div style={styles.cardActions}>
        <button
          onClick={() => navigate(`/result/${job.project_id}`)}
          style={{...styles.actionBtn, background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)'}}
        >
          📺 RESULT
        </button>
        <button
          onClick={() => navigate(`/generate/${job.project_id}`)}
          style={{...styles.actionBtn, background: 'linear-gradient(135deg, #FFE66D 0%, #F9CA24 100%)'}}
        >
          ⚙️ PROGRESS
        </button>
        <button
          onClick={() => onViewDetail(job.id)}
          style={{...styles.actionBtn, background: 'linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)'}}
        >
          📋 DETAIL
        </button>
        {job.status === 'failed' && (
          <button
            onClick={() => onRetry(job.id)}
            style={{...styles.actionBtn, background: 'linear-gradient(135deg, #F38181 0%, #FCE38A 100%)'}}
          >
            🔄 RETRY
          </button>
        )}
        {job.status === 'running' && (
          <button
            onClick={() => onCancel(job.id)}
            style={{...styles.actionBtn, background: 'linear-gradient(135deg, #666 0%, #999 100%)'}}
          >
            ⛔ CANCEL
          </button>
        )}
      </div>
    </div>
  )
}

// Progress Bar Component
function ProgressBar({ progress, status }) {
  const percentage = Math.round(progress * 100)

  const gradients = {
    running: 'linear-gradient(90deg, #FFE66D 0%, #F9CA24 100%)',
    completed: 'linear-gradient(90deg, #95E1D3 0%, #44A08D 100%)',
    failed: 'linear-gradient(90deg, #FF6B6B 0%, #C44569 100%)',
    default: 'linear-gradient(90deg, #4ECDC4 0%, #44A08D 100%)'
  }

  return (
    <div style={styles.progressContainer}>
      <div style={{
        ...styles.progressBar,
        width: `${percentage}%`,
        background: gradients[status] || gradients.default,
        boxShadow: percentage > 0 ? `0 0 10px ${status === 'running' ? '#FFE66D' : '#4ECDC4'}66` : 'none'
      }} />
      <span style={styles.progressText}>{percentage}%</span>
    </div>
  )
}

// Job Detail Modal Component
function JobDetailModal({ job, onClose, navigate }) {
  const [scenes, setScenes] = useState([])
  const [loadingScenes, setLoadingScenes] = useState(false)

  useEffect(() => {
    const loadScenes = async () => {
      try {
        setLoadingScenes(true)
        const response = await axios.get(`${API_BASE}/projects/${job.project_id}/scenes`)
        setScenes(response.data)
      } catch (error) {
        console.error('Failed to load scenes:', error)
      } finally {
        setLoadingScenes(false)
      }
    }

    if (job.project_id) {
      loadScenes()
    }
  }, [job.project_id])

  const statusConfig = {
    completed: { icon: '✓', label: 'COMPLETED', color: '#95E1D3' },
    running: { icon: '⟳', label: 'RUNNING', color: '#FFE66D' },
    failed: { icon: '✕', label: 'FAILED', color: '#FF6B6B' },
    cancelled: { icon: '○', label: 'CANCELLED', color: '#888' },
    pending: { icon: '◷', label: 'PENDING', color: '#4ECDC4' }
  }

  const config = statusConfig[job.status] || statusConfig.pending

  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <h2 style={styles.modalTitle}>JOB DETAILS</h2>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>

        <div style={styles.modalBody}>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>JOB ID</span>
            <code style={styles.code}>{job.id}</code>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>PROJECT ID</span>
            <code style={styles.code}>{job.project_id}</code>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>TYPE</span>
            <span style={styles.detailValue}>{job.job_type}</span>
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>STATUS</span>
            <span style={{ ...styles.detailValue, color: config.color }}>
              {config.icon} {config.label}
            </span>
          </div>
          {job.stage && (
            <div style={styles.detailRow}>
              <span style={styles.detailLabel}>STAGE</span>
              <span style={styles.detailValue}>{job.stage}</span>
            </div>
          )}
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>PROGRESS</span>
            <ProgressBar progress={job.progress || 0} status={job.status} />
          </div>
          <div style={styles.detailRow}>
            <span style={styles.detailLabel}>CREATED</span>
            <span style={styles.detailValue}>{formatLocalTime(job.created_at)}</span>
          </div>
          {job.error_message && (
            <div style={styles.detailRow}>
              <span style={styles.detailLabel}>ERROR</span>
              <pre style={styles.errorPre}>{job.error_message}</pre>
            </div>
          )}
          {job.result_data && (
            <div style={styles.detailRow}>
              <span style={styles.detailLabel}>RESULT DATA</span>
              <pre style={styles.pre}>{JSON.stringify(job.result_data, null, 2)}</pre>
            </div>
          )}

          {/* Quick actions */}
          <div style={styles.quickActions}>
            <button
              onClick={() => navigate(`/result/${job.project_id}`)}
              style={{...styles.quickButton, background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)'}}
            >
              <span style={styles.quickButtonIcon}>📺</span>
              <span>VIEW RESULT</span>
            </button>
            <button
              onClick={() => navigate(`/generate/${job.project_id}`)}
              style={{...styles.quickButton, background: 'linear-gradient(135deg, #FFE66D 0%, #F9CA24 100%)'}}
            >
              <span style={styles.quickButtonIcon}>⚙️</span>
              <span>GENERATION</span>
            </button>
          </div>

          {/* Scenes list */}
          {loadingScenes ? (
            <div style={styles.scenesLoading}>⚙️ Loading scenes...</div>
          ) : scenes.length > 0 ? (
            <div style={styles.scenesSection}>
              <h3 style={styles.sectionTitle}>SCENES</h3>
              <div style={styles.scenesList}>
                {scenes.map((scene, index) => (
                  <div key={scene.scene_id} style={styles.sceneItem}>
                    <div style={styles.sceneInfo}>
                      <span style={styles.sceneNumber}>SCENE {index + 1}</span>
                      <span style={styles.sceneType}>{scene.template_type}</span>
                    </div>
                    <button
                      onClick={() => navigate(`/timeline-editor/${scene.scene_id}`)}
                      style={{...styles.sceneButton, background: 'linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)'}}
                    >
                      🎬 EDIT TIMELINE
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

// Helper functions
function getFilterName(filter) {
  const names = {
    running: 'running',
    completed: 'completed',
    failed: 'failed'
  }
  return names[filter] || ''
}

// Styles
const styles = {
  container: {
    padding: '0',
    position: 'relative',
    minHeight: '100vh'
  },
  filmStripLeft: {
    position: 'fixed',
    left: 0,
    top: 0,
    bottom: 0,
    width: '8px',
    background: 'repeating-linear-gradient(0deg, #FF6B6B 0px, #FF6B6B 20px, transparent 20px, transparent 40px)',
    zIndex: 10,
    pointerEvents: 'none'
  },
  filmStripRight: {
    position: 'fixed',
    right: 0,
    top: 0,
    bottom: 0,
    width: '8px',
    background: 'repeating-linear-gradient(0deg, #4ECDC4 0px, #4ECDC4 20px, transparent 20px, transparent 40px)',
    zIndex: 10,
    pointerEvents: 'none'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px',
    flexWrap: 'wrap',
    gap: '16px'
  },
  filters: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap'
  },
  filterButton: {
    padding: '12px 20px',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '700',
    color: '#CCCCCC',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  filterLabel: {
    fontSize: '13px'
  },
  filterCount: {
    fontSize: '12px',
    fontWeight: '900'
  },

  actions: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center'
  },
  autoRefreshLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    padding: '10px 16px',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    transition: 'all 0.2s'
  },
  checkbox: {
    cursor: 'pointer',
    width: '16px',
    height: '16px'
  },
  autoRefreshText: {
    fontSize: '13px',
    color: '#CCCCCC',
    fontWeight: '700',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1px'
  },
  refreshButton: {
    padding: '10px 20px',
    background: 'linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)',
    color: '#0F0F0F',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '700',
    transition: 'all 0.2s',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1px',
    boxShadow: '0 0 20px rgba(78, 205, 196, 0.3)'
  },
  loading: {
    textAlign: 'center',
    padding: '80px',
    color: '#4ECDC4',
    fontSize: '16px',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '2px',
    fontWeight: '700'
  },
  empty: {
    textAlign: 'center',
    padding: '80px 20px',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: '16px',
    border: '2px solid rgba(255, 255, 255, 0.1)'
  },
  emptyIcon: {
    fontSize: '64px',
    marginBottom: '16px'
  },
  emptyTitle: {
    fontSize: '20px',
    fontWeight: '900',
    color: '#FFFFFF',
    marginBottom: '8px',
    fontFamily: '"Playfair Display", Georgia, serif',
    letterSpacing: '2px'
  },
  emptyText: {
    fontSize: '14px',
    color: '#888888',
    fontFamily: 'Monaco, "Courier New", monospace'
  },

  jobsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
    gap: '24px'
  },
  jobCard: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '24px',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
    cursor: 'pointer'
  },
  statusBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    borderRadius: '20px',
    fontSize: '12px',
    fontWeight: '700',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1px',
    border: '2px solid',
    marginBottom: '16px'
  },
  statusText: {
    fontSize: '12px'
  },
  jobInfo: {
    marginBottom: '20px'
  },
  jobId: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px'
  },
  jobIdLabel: {
    fontSize: '11px',
    fontWeight: '900',
    color: '#888888',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1.5px'
  },
  code: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: '6px 12px',
    borderRadius: '6px',
    fontSize: '13px',
    fontFamily: 'Monaco, "Courier New", monospace',
    color: '#4ECDC4',
    fontWeight: '700',
    border: '1px solid rgba(78, 205, 196, 0.3)'
  },
  jobMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    marginBottom: '8px'
  },
  metaItem: {
    fontSize: '13px',
    color: '#CCCCCC',
    fontFamily: 'Monaco, "Courier New", monospace'
  },
  jobTime: {
    fontSize: '12px',
    color: '#888888',
    fontFamily: 'Monaco, "Courier New", monospace'
  },

  progressContainer: {
    position: 'relative',
    width: '100%',
    height: '32px',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '16px',
    overflow: 'hidden',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    marginBottom: '20px'
  },
  progressBar: {
    height: '100%',
    transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
    borderRadius: '16px'
  },
  progressText: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    fontSize: '12px',
    fontWeight: '900',
    color: '#FFFFFF',
    fontFamily: 'Monaco, "Courier New", monospace',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.5)',
    letterSpacing: '1px'
  },
  cardActions: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px'
  },
  actionBtn: {
    padding: '10px 16px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '700',
    transition: 'all 0.2s',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '0.5px',
    color: '#0F0F0F',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
    flex: '1 1 auto',
    minWidth: '100px'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    backdropFilter: 'blur(8px)'
  },
  modal: {
    backgroundColor: '#1A1A1A',
    borderRadius: '16px',
    maxWidth: '800px',
    width: '90%',
    maxHeight: '85vh',
    overflow: 'auto',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(78, 205, 196, 0.2)',
    border: '2px solid rgba(78, 205, 196, 0.3)'
  },

  modalHeader: {
    padding: '24px 28px',
    borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: 'linear-gradient(135deg, rgba(78, 205, 196, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%)'
  },
  modalTitle: {
    margin: 0,
    fontSize: '24px',
    fontWeight: '900',
    fontFamily: '"Playfair Display", Georgia, serif',
    color: '#FFFFFF',
    letterSpacing: '2px',
    textShadow: '0 0 20px rgba(78, 205, 196, 0.5)'
  },
  closeButton: {
    backgroundColor: 'transparent',
    border: 'none',
    fontSize: '32px',
    cursor: 'pointer',
    color: '#888888',
    lineHeight: 1,
    padding: '0',
    width: '40px',
    height: '40px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '8px',
    transition: 'all 0.2s'
  },
  modalBody: {
    padding: '28px'
  },
  detailRow: {
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  detailLabel: {
    fontSize: '11px',
    fontWeight: '900',
    color: '#888888',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1.5px'
  },
  detailValue: {
    fontSize: '14px',
    color: '#FFFFFF',
    fontFamily: 'Monaco, "Courier New", monospace'
  },
  pre: {
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    padding: '16px',
    borderRadius: '10px',
    fontSize: '13px',
    overflow: 'auto',
    maxHeight: '250px',
    fontFamily: 'Monaco, "Courier New", monospace',
    color: '#CCCCCC',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    lineHeight: '1.6'
  },
  errorPre: {
    backgroundColor: 'rgba(255, 107, 107, 0.1)',
    padding: '16px',
    borderRadius: '10px',
    fontSize: '13px',
    overflow: 'auto',
    maxHeight: '250px',
    color: '#FF6B6B',
    fontFamily: 'Monaco, "Courier New", monospace',
    border: '1px solid rgba(255, 107, 107, 0.3)',
    lineHeight: '1.6'
  },

  quickActions: {
    marginTop: '28px',
    display: 'flex',
    gap: '12px'
  },
  quickButton: {
    flex: 1,
    padding: '16px',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    transition: 'all 0.2s',
    fontFamily: 'Monaco, "Courier New", monospace',
    fontSize: '13px',
    fontWeight: '700',
    color: '#0F0F0F',
    letterSpacing: '1px',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
  },
  quickButtonIcon: {
    fontSize: '28px'
  },
  scenesSection: {
    marginTop: '28px',
    paddingTop: '28px',
    borderTop: '2px solid rgba(255, 255, 255, 0.1)'
  },
  sectionTitle: {
    margin: '0 0 16px 0',
    fontSize: '16px',
    fontWeight: '900',
    fontFamily: 'Monaco, "Courier New", monospace',
    color: '#FFFFFF',
    letterSpacing: '2px'
  },
  scenesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  sceneItem: {
    padding: '16px',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: '12px',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    transition: 'all 0.2s'
  },
  sceneInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  sceneNumber: {
    fontSize: '14px',
    fontWeight: '700',
    color: '#FFFFFF',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '1px'
  },
  sceneType: {
    fontSize: '13px',
    color: '#888888',
    fontFamily: 'Monaco, "Courier New", monospace'
  },
  sceneButton: {
    padding: '10px 18px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: '700',
    transition: 'all 0.2s',
    fontFamily: 'Monaco, "Courier New", monospace',
    letterSpacing: '0.5px',
    color: '#0F0F0F',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
  },
  scenesLoading: {
    textAlign: 'center',
    padding: '24px',
    color: '#888888',
    fontSize: '14px',
    fontFamily: 'Monaco, "Courier New", monospace'
  }
}

export default JobsManager_Cinema

