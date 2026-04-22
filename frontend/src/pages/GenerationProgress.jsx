/**
 * Editorial Studio - Generation Progress Page
 * 优雅的进度展示页面，实时显示 AI 创作过程
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function GenerationProgress() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState('initializing')
  const [stage, setStage] = useState('')
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState(null)

  // Start generation job
  useEffect(() => {
    const startGeneration = async () => {
      try {
        const response = await axios.post(
          `${API_BASE}/projects/${projectId}/jobs/generate`
        )
        setJobId(response.data.job_id)
        setStatus(response.data.status)
      } catch (err) {
        setError(err.response?.data?.detail || '启动生成任务失败')
        console.error('Error starting generation:', err)
      }
    }

    if (projectId) {
      startGeneration()
    }
  }, [projectId])

  // Poll job status
  useEffect(() => {
    if (!jobId) return

    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_BASE}/jobs/${jobId}`)
        const jobData = response.data

        setStatus(jobData.status)
        setStage(jobData.stage || '')
        setProgress(jobData.progress || 0)

        if (jobData.error) {
          // Convert error object to string if needed
          const errorMsg = typeof jobData.error === 'object'
            ? (jobData.error.message || JSON.stringify(jobData.error))
            : jobData.error
          setError(errorMsg)
        }

        // Stop polling if completed or failed
        if (jobData.status === 'completed') {
          clearInterval(pollInterval)
          // Navigate to result page after a short delay
          setTimeout(() => {
            navigate(`/result/${projectId}`)
          }, 1500)
        } else if (jobData.status === 'failed') {
          clearInterval(pollInterval)
          // Convert error object to string if needed
          const errorMsg = jobData.error
            ? (typeof jobData.error === 'object'
                ? (jobData.error.message || JSON.stringify(jobData.error))
                : jobData.error)
            : '生成失败'
          setError(errorMsg)
        }
      } catch (err) {
        console.error('Error polling job status:', err)
      }
    }, 2000)

    return () => clearInterval(pollInterval)
  }, [jobId, projectId, navigate])

  const getStageText = (stage) => {
    const stageMap = {
      'parsing': '解析文章',
      'scene_generation': '生成场景',
      'tts': '生成语音',
      'subtitle': '生成字幕',
      'rendering': '渲染视频',
      'export': '导出视频'
    }
    return stageMap[stage] || stage
  }

  const getStatusText = (status) => {
    const statusMap = {
      'initializing': '初始化中...',
      'queued': '排队中...',
      'running': '生成中...',
      'completed': '完成！',
      'failed': '失败'
    }
    return statusMap[status] || status
  }

  return (
    <div style={styles.container}>
      {/* Hero Section */}
      <div style={styles.hero}>
        <div style={styles.heroNumber}>02</div>
        <h1 style={styles.heroTitle}>
          Creating Your
          <br />
          Visual Story
        </h1>
        <p style={styles.heroSubtitle}>
          AI 正在分析内容并生成精美视频
        </p>
      </div>

      {/* Progress Card */}
      <div style={styles.progressCard}>
        {/* Status Display */}
        <div style={styles.statusSection}>
          <div style={styles.statusLabel}>当前状态</div>
          <div style={styles.statusValue}>{getStatusText(status)}</div>
        </div>

        {/* Stage Display */}
        {stage && (
          <div style={styles.stageSection}>
            <div style={styles.stageLabel}>处理阶段</div>
            <div style={styles.stageValue}>{getStageText(stage)}</div>
          </div>
        )}

        {/* Progress Bar */}
        <div style={styles.progressSection}>
          <div style={styles.progressHeader}>
            <span style={styles.progressLabel}>完成进度</span>
            <span style={styles.progressPercentage}>
              {Math.round(progress * 100)}%
            </span>
          </div>
          <div style={styles.progressBarContainer}>
            <div
              style={{
                ...styles.progressBarFill,
                width: `${progress * 100}%`
              }}
            />
          </div>
        </div>

        {/* Timeline Steps */}
        <div style={styles.timeline}>
          <TimelineStep
            number="1"
            label="解析文章"
            active={stage === 'parsing'}
            completed={['scene_generation', 'tts', 'subtitle', 'rendering', 'export'].includes(stage)}
          />
          <TimelineStep
            number="2"
            label="生成场景"
            active={stage === 'scene_generation'}
            completed={['tts', 'subtitle', 'rendering', 'export'].includes(stage)}
          />
          <TimelineStep
            number="3"
            label="生成语音"
            active={stage === 'tts'}
            completed={['subtitle', 'rendering', 'export'].includes(stage)}
          />
          <TimelineStep
            number="4"
            label="生成字幕"
            active={stage === 'subtitle'}
            completed={['rendering', 'export'].includes(stage)}
          />
          <TimelineStep
            number="5"
            label="渲染视频"
            active={stage === 'rendering'}
            completed={stage === 'export'}
          />
          <TimelineStep
            number="6"
            label="导出完成"
            active={stage === 'export'}
            completed={status === 'completed'}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div style={styles.errorBox}>
            <div style={styles.errorIcon}>⚠</div>
            <div>
              <div style={styles.errorTitle}>生成失败</div>
              <div style={styles.errorMessage}>{error}</div>
            </div>
          </div>
        )}

        {/* Success Message */}
        {status === 'completed' && (
          <div style={styles.successBox}>
            <div style={styles.successIcon}>✓</div>
            <div style={styles.successText}>
              视频生成完成！正在跳转到结果页面...
            </div>
          </div>
        )}

        {/* Info Section */}
        <div style={styles.infoSection}>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>项目 ID:</span>
            <code style={styles.infoValue}>{projectId}</code>
          </div>
          {jobId && (
            <div style={styles.infoItem}>
              <span style={styles.infoLabel}>任务 ID:</span>
              <code style={styles.infoValue}>{jobId}</code>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div style={styles.actions}>
        <button
          onClick={() => navigate('/')}
          style={styles.backButton}
        >
          ← 返回首页
        </button>
        <button
          onClick={() => navigate(`/result/${projectId}`)}
          style={styles.viewButton}
          disabled={status !== 'completed'}
        >
          查看结果 →
        </button>
      </div>
    </div>
  )
}

// Timeline Step Component
function TimelineStep({ number, label, active, completed }) {
  return (
    <div style={styles.timelineStep}>
      <div style={{
        ...styles.timelineNumber,
        backgroundColor: completed ? '#D4A574' : active ? '#2C2416' : '#E8E6E0',
        color: completed || active ? '#FFFFFF' : '#9B9388'
      }}>
        {completed ? '✓' : number}
      </div>
      <div style={{
        ...styles.timelineLabel,
        color: completed || active ? '#2C2416' : '#9B9388',
        fontWeight: active ? '600' : '400'
      }}>
        {label}
      </div>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '80px 40px 120px'
  },

  // Hero Section
  hero: {
    marginBottom: '60px',
    textAlign: 'center'
  },
  heroNumber: {
    fontSize: '120px',
    fontWeight: '300',
    color: '#F5F4F0',
    lineHeight: 1,
    marginBottom: '-40px',
    fontFamily: 'Georgia, "Times New Roman", serif',
    letterSpacing: '-0.02em'
  },
  heroTitle: {
    fontSize: '56px',
    fontWeight: '400',
    fontFamily: 'Georgia, "Times New Roman", serif',
    color: '#2C2416',
    lineHeight: 1.2,
    marginBottom: '24px',
    letterSpacing: '-0.01em'
  },
  heroSubtitle: {
    fontSize: '18px',
    color: '#6B6456',
    lineHeight: 1.6,
    fontWeight: '400'
  },

  // Progress Card
  progressCard: {
    backgroundColor: '#FFFFFF',
    border: '2px solid #E8E6E0',
    borderRadius: '16px',
    padding: '48px',
    marginBottom: '40px'
  },

  // Status Section
  statusSection: {
    marginBottom: '32px',
    paddingBottom: '32px',
    borderBottom: '1px solid #E8E6E0'
  },
  statusLabel: {
    fontSize: '13px',
    fontWeight: '600',
    color: '#9B9388',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    marginBottom: '8px'
  },
  statusValue: {
    fontSize: '28px',
    fontWeight: '600',
    color: '#2C2416',
    fontFamily: 'Georgia, serif'
  },

  // Stage Section
  stageSection: {
    marginBottom: '32px',
    paddingBottom: '32px',
    borderBottom: '1px solid #E8E6E0'
  },
  stageLabel: {
    fontSize: '13px',
    fontWeight: '600',
    color: '#9B9388',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    marginBottom: '8px'
  },
  stageValue: {
    fontSize: '20px',
    fontWeight: '500',
    color: '#D4A574'
  },

  // Progress Section
  progressSection: {
    marginBottom: '48px'
  },
  progressHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: '16px'
  },
  progressLabel: {
    fontSize: '13px',
    fontWeight: '600',
    color: '#9B9388',
    textTransform: 'uppercase',
    letterSpacing: '1px'
  },
  progressPercentage: {
    fontSize: '32px',
    fontWeight: '600',
    color: '#2C2416',
    fontFamily: 'Georgia, serif'
  },
  progressBarContainer: {
    width: '100%',
    height: '12px',
    backgroundColor: '#F5F4F0',
    borderRadius: '6px',
    overflow: 'hidden'
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#D4A574',
    transition: 'width 0.5s ease',
    borderRadius: '6px'
  },

  // Timeline
  timeline: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '24px',
    marginBottom: '48px'
  },
  timelineStep: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px'
  },
  timelineNumber: {
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    fontWeight: '600',
    transition: 'all 0.3s ease'
  },
  timelineLabel: {
    fontSize: '13px',
    textAlign: 'center',
    transition: 'all 0.3s ease'
  },

  // Error Box
  errorBox: {
    display: 'flex',
    gap: '16px',
    padding: '24px',
    backgroundColor: '#FEF2F2',
    border: '2px solid #FCA5A5',
    borderRadius: '12px',
    marginBottom: '24px'
  },
  errorIcon: {
    fontSize: '24px',
    color: '#DC2626'
  },
  errorTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#DC2626',
    marginBottom: '4px'
  },
  errorMessage: {
    fontSize: '14px',
    color: '#991B1B',
    lineHeight: 1.6
  },

  // Success Box
  successBox: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    padding: '24px',
    backgroundColor: '#F0FDF4',
    border: '2px solid #86EFAC',
    borderRadius: '12px',
    marginBottom: '24px'
  },
  successIcon: {
    fontSize: '32px',
    color: '#16A34A'
  },
  successText: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#166534'
  },

  // Info Section
  infoSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    padding: '20px',
    backgroundColor: '#FAF9F6',
    borderRadius: '8px'
  },
  infoItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '14px'
  },
  infoLabel: {
    color: '#9B9388',
    fontWeight: '500'
  },
  infoValue: {
    fontFamily: 'Monaco, "Courier New", monospace',
    fontSize: '13px',
    color: '#2C2416',
    backgroundColor: '#FFFFFF',
    padding: '4px 8px',
    borderRadius: '4px',
    border: '1px solid #E8E6E0'
  },

  // Actions
  actions: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center'
  },
  backButton: {
    padding: '16px 32px',
    fontSize: '16px',
    fontWeight: '500',
    color: '#6B6456',
    backgroundColor: '#FFFFFF',
    border: '2px solid #E8E6E0',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s ease'
  },
  viewButton: {
    padding: '16px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#FFFFFF',
    backgroundColor: '#2C2416',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 16px rgba(44, 36, 22, 0.2)'
  }
}

export default GenerationProgress
