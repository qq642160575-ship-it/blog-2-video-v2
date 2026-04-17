import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

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
          `${API_BASE_URL}/projects/${projectId}/jobs/generate`
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
        const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`)
        const jobData = response.data

        setStatus(jobData.status)
        setStage(jobData.stage || '')
        setProgress(jobData.progress || 0)

        if (jobData.error) {
          setError(jobData.error)
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
          setError(jobData.error || '生成失败')
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
    <div style={styles.container} className="fade-in">
      <div style={styles.header}>
        <h1 style={styles.title}>🎬 视频生成中</h1>
        <p style={styles.subtitle}>AI正在为您创作精彩内容，请稍候...</p>
      </div>

      <div style={styles.card}>
        <div style={styles.statusSection}>
          <div style={styles.statusText}>
            {getStatusText(status)}
          </div>
          {stage && (
            <div style={styles.stageText}>
              当前阶段: {getStageText(stage)}
            </div>
          )}
        </div>

        <div style={styles.progressSection}>
          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${progress * 100}%`
              }}
            />
          </div>
          <div style={styles.progressText}>
            {Math.round(progress * 100)}%
          </div>
        </div>

        {error && (
          <div style={styles.error}>
            <strong>错误:</strong> {error}
          </div>
        )}

        {status === 'completed' && (
          <div style={styles.success}>
            ✓ 视频生成完成！正在跳转到结果页面...
          </div>
        )}

        <div style={styles.info}>
          <div>项目 ID: {projectId}</div>
          {jobId && <div>任务 ID: {jobId}</div>}
        </div>
      </div>

      <button
        onClick={() => navigate('/')}
        style={styles.backButton}
      >
        返回首页
      </button>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '700px',
    margin: '0 auto',
    padding: '40px 20px'
  },
  header: {
    textAlign: 'center',
    marginBottom: '40px'
  },
  title: {
    fontSize: '42px',
    fontWeight: 'bold',
    marginBottom: '12px',
    color: 'white',
    textShadow: '0 2px 10px rgba(0, 0, 0, 0.2)'
  },
  subtitle: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.9)',
    margin: 0
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '16px',
    padding: '40px',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)'
  },
  statusSection: {
    marginBottom: '40px',
    textAlign: 'center'
  },
  statusText: {
    fontSize: '28px',
    fontWeight: '600',
    color: '#333',
    marginBottom: '12px'
  },
  stageText: {
    fontSize: '18px',
    color: '#666',
    padding: '8px 16px',
    backgroundColor: '#f0f0f0',
    borderRadius: '20px',
    display: 'inline-block'
  },
  progressSection: {
    marginBottom: '30px'
  },
  progressBar: {
    width: '100%',
    height: '28px',
    backgroundColor: '#e8e8e8',
    borderRadius: '14px',
    overflow: 'hidden',
    marginBottom: '12px',
    position: 'relative'
  },
  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
    transition: 'width 0.5s ease',
    borderRadius: '14px',
    position: 'relative',
    overflow: 'hidden'
  },
  progressText: {
    textAlign: 'center',
    fontSize: '20px',
    fontWeight: '600',
    color: '#333'
  },
  error: {
    padding: '16px 20px',
    backgroundColor: '#fee',
    color: '#c33',
    borderRadius: '10px',
    border: '2px solid #fcc',
    marginTop: '20px',
    fontSize: '15px'
  },
  success: {
    padding: '20px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '10px',
    border: '2px solid #c3e6cb',
    marginTop: '20px',
    textAlign: 'center',
    fontSize: '18px',
    fontWeight: '500'
  },
  info: {
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '10px',
    fontSize: '14px',
    color: '#666',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  backButton: {
    marginTop: '30px',
    padding: '14px 28px',
    fontSize: '16px',
    fontWeight: '500',
    color: '#666',
    backgroundColor: 'white',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    cursor: 'pointer',
    display: 'block',
    margin: '30px auto 0',
    transition: 'all 0.3s'
  }
}

export default GenerationProgress
