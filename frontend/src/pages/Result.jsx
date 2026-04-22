/**
 * input: 依赖结果查询 API 和路由参数。
 * output: 向外提供生成结果页面。
 * pos: 位于前端页面层，负责结果展示。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

function Result() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [scenes, setScenes] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch video result
        const resultResponse = await axios.get(
          `${API_BASE_URL}/projects/${projectId}/result`
        )
        setVideoUrl(resultResponse.data.video_url)

        // Fetch scenes
        const scenesResponse = await axios.get(
          `${API_BASE_URL}/projects/${projectId}/scenes`
        )
        setScenes(scenesResponse.data)

        setLoading(false)
      } catch (err) {
        setError(err.response?.data?.detail || '加载失败')
        setLoading(false)
        console.error('Error fetching result:', err)
      }
    }

    if (projectId) {
      fetchData()
    }
  }, [projectId])

  const handleRerender = async () => {
    try {
      await axios.post(`${API_BASE_URL}/projects/${projectId}/jobs/rerender`)
      navigate(`/generate/${projectId}`)
    } catch (err) {
      alert('触发重渲染失败: ' + (err.response?.data?.detail || err.message))
    }
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loadingBox}>
          <div style={styles.loadingSpinner}></div>
          <div style={styles.loadingText}>加载中...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.errorBox}>
          <div style={styles.errorTitle}>加载失败</div>
          <div style={styles.errorMessage}>{error}</div>
          <button onClick={() => navigate('/')} style={styles.primaryButton}>
            返回首页
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      {/* Hero Section */}
      <div style={styles.hero}>
        <div style={styles.heroNumber}>03</div>
        <h1 style={styles.heroTitle}>
          Your Visual Story<br />Is Ready
        </h1>
        <div style={styles.heroSubtitle}>视频已生成完成</div>
      </div>

      {/* Video Player Section */}
      <div style={styles.videoSection}>
        <div style={styles.sectionLabel}>
          <span style={styles.labelNumber}>3.1</span>
          <span style={styles.labelText}>视频预览</span>
        </div>

        <div style={styles.videoContainer}>
          {videoUrl ? (
            <video
              controls
              style={styles.video}
              src={`${API_BASE_URL}${videoUrl}`}
            >
              您的浏览器不支持视频播放
            </video>
          ) : (
            <div style={styles.noVideo}>视频未生成</div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div style={styles.actions}>
        <button onClick={handleRerender} style={styles.primaryButton}>
          重新渲染
        </button>
        <button onClick={() => navigate('/')} style={styles.secondaryButton}>
          创建新项目
        </button>
      </div>

      {/* Scenes Section */}
      {scenes.length > 0 && (
        <div style={styles.scenesSection}>
          <div style={styles.sectionLabel}>
            <span style={styles.labelNumber}>3.2</span>
            <span style={styles.labelText}>场景详情</span>
            <span style={styles.sceneCount}>({scenes.length})</span>
          </div>

          <div style={styles.scenesList}>
            {scenes.map((scene, index) => (
              <SceneCard
                key={scene.scene_id}
                scene={scene}
                index={index}
                navigate={navigate}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Scene Card Component
function SceneCard({ scene, index, navigate }) {
  return (
    <div style={styles.sceneCard}>
      <div style={styles.sceneCardHeader}>
        <div style={styles.sceneCardLeft}>
          <div style={styles.sceneIndexNumber}>{String(index + 1).padStart(2, '0')}</div>
          <div>
            <div style={styles.sceneTitle}>场景 {index + 1}</div>
            <div style={styles.sceneVersion}>版本 {scene.version}</div>
          </div>
        </div>
        <div style={styles.sceneCardActions}>
          <button
            onClick={() => navigate(`/edit-scene/${scene.scene_id}`)}
            style={styles.sceneButton}
          >
            编辑场景
          </button>
          <button
            onClick={() => navigate(`/timeline-editor/${scene.scene_id}`)}
            style={styles.sceneButton}
          >
            时间轴
          </button>
        </div>
      </div>

      <div style={styles.sceneCardBody}>
        <div style={styles.sceneMetaRow}>
          <div style={styles.sceneMeta}>
            <span style={styles.sceneMetaLabel}>模板</span>
            <span style={styles.sceneMetaValue}>{scene.template_type}</span>
          </div>
          <div style={styles.sceneMeta}>
            <span style={styles.sceneMetaLabel}>时长</span>
            <span style={styles.sceneMetaValue}>{scene.duration_sec}秒</span>
          </div>
        </div>

        <div style={styles.sceneVoiceover}>
          <div style={styles.sceneContentLabel}>旁白</div>
          <div style={styles.voiceoverText}>{scene.voiceover}</div>
        </div>

        {scene.screen_text && scene.screen_text.length > 0 && (
          <div style={styles.sceneScreenText}>
            <div style={styles.sceneContentLabel}>屏幕文本</div>
            <div style={styles.screenTextList}>
              {scene.screen_text.map((text, i) => (
                <div key={i} style={styles.screenTextTag}>
                  {text}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    padding: '60px 24px 100px',
    backgroundColor: '#FAF9F6',
    minHeight: '100vh'
  },

  // Hero Section
  hero: {
    textAlign: 'center',
    marginBottom: '80px',
    position: 'relative'
  },
  heroNumber: {
    fontSize: '180px',
    fontWeight: '300',
    color: '#E8E6E0',
    lineHeight: '1',
    marginBottom: '-40px',
    fontFamily: 'Georgia, "Times New Roman", serif',
    userSelect: 'none'
  },
  heroTitle: {
    fontSize: '56px',
    fontWeight: '300',
    color: '#2C2416',
    lineHeight: '1.2',
    marginBottom: '16px',
    fontFamily: 'Georgia, "Times New Roman", serif',
    letterSpacing: '-0.02em'
  },
  heroSubtitle: {
    fontSize: '14px',
    color: '#8B7355',
    textTransform: 'uppercase',
    letterSpacing: '0.15em',
    fontWeight: '500'
  },

  // Loading & Error States
  loadingBox: {
    textAlign: 'center',
    padding: '100px 20px'
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
    fontSize: '16px',
    color: '#8B7355',
    letterSpacing: '0.05em'
  },
  errorBox: {
    textAlign: 'center',
    padding: '60px 40px',
    backgroundColor: '#FFFFFF',
    border: '1px solid #E8E6E0',
    maxWidth: '500px',
    margin: '100px auto'
  },
  errorTitle: {
    fontSize: '24px',
    fontWeight: '300',
    color: '#2C2416',
    marginBottom: '12px',
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  errorMessage: {
    fontSize: '15px',
    color: '#8B7355',
    marginBottom: '32px',
    lineHeight: '1.6'
  },

  // Section Labels
  sectionLabel: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '12px',
    marginBottom: '24px'
  },
  labelNumber: {
    fontSize: '13px',
    color: '#D4A574',
    fontWeight: '600',
    letterSpacing: '0.05em'
  },
  labelText: {
    fontSize: '13px',
    color: '#2C2416',
    textTransform: 'uppercase',
    letterSpacing: '0.15em',
    fontWeight: '500'
  },
  sceneCount: {
    fontSize: '13px',
    color: '#8B7355',
    marginLeft: '4px'
  },

  // Video Section
  videoSection: {
    marginBottom: '60px'
  },
  videoContainer: {
    backgroundColor: '#000000',
    border: '1px solid #E8E6E0',
    overflow: 'hidden',
    position: 'relative'
  },
  video: {
    width: '100%',
    display: 'block',
    maxHeight: '600px'
  },
  noVideo: {
    padding: '100px 20px',
    textAlign: 'center',
    color: '#8B7355',
    fontSize: '15px',
    letterSpacing: '0.05em'
  },

  // Actions
  actions: {
    display: 'flex',
    gap: '16px',
    justifyContent: 'center',
    marginBottom: '80px'
  },
  primaryButton: {
    padding: '16px 40px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#FFFFFF',
    backgroundColor: '#2C2416',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },
  secondaryButton: {
    padding: '16px 40px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#2C2416',
    backgroundColor: 'transparent',
    border: '1px solid #2C2416',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },

  // Scenes Section
  scenesSection: {
    marginTop: '80px'
  },
  scenesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '32px'
  },

  // Scene Card
  sceneCard: {
    backgroundColor: '#FFFFFF',
    border: '1px solid #E8E6E0',
    padding: '40px',
    transition: 'all 0.3s ease'
  },
  sceneCardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '32px',
    paddingBottom: '24px',
    borderBottom: '1px solid #E8E6E0'
  },
  sceneCardLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px'
  },
  sceneIndexNumber: {
    fontSize: '48px',
    fontWeight: '300',
    color: '#D4A574',
    fontFamily: 'Georgia, "Times New Roman", serif',
    lineHeight: '1'
  },
  sceneTitle: {
    fontSize: '18px',
    fontWeight: '300',
    color: '#2C2416',
    marginBottom: '4px',
    fontFamily: 'Georgia, "Times New Roman", serif'
  },
  sceneVersion: {
    fontSize: '12px',
    color: '#8B7355',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },
  sceneCardActions: {
    display: 'flex',
    gap: '12px'
  },
  sceneButton: {
    padding: '10px 20px',
    fontSize: '12px',
    fontWeight: '500',
    color: '#2C2416',
    backgroundColor: 'transparent',
    border: '1px solid #E8E6E0',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },

  // Scene Card Body
  sceneCardBody: {
    display: 'flex',
    flexDirection: 'column',
    gap: '28px'
  },
  sceneMetaRow: {
    display: 'flex',
    gap: '40px'
  },
  sceneMeta: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  sceneMetaLabel: {
    fontSize: '11px',
    color: '#8B7355',
    textTransform: 'uppercase',
    letterSpacing: '0.15em',
    fontWeight: '500'
  },
  sceneMetaValue: {
    fontSize: '15px',
    color: '#2C2416',
    fontWeight: '400'
  },

  // Scene Content
  sceneVoiceover: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  sceneContentLabel: {
    fontSize: '11px',
    color: '#8B7355',
    textTransform: 'uppercase',
    letterSpacing: '0.15em',
    fontWeight: '500'
  },
  voiceoverText: {
    fontSize: '15px',
    lineHeight: '1.8',
    color: '#2C2416',
    padding: '20px',
    backgroundColor: '#FAF9F6',
    border: '1px solid #E8E6E0'
  },

  // Screen Text
  sceneScreenText: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px'
  },
  screenTextList: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px'
  },
  screenTextTag: {
    padding: '8px 16px',
    fontSize: '13px',
    color: '#2C2416',
    backgroundColor: '#FAF9F6',
    border: '1px solid #E8E6E0',
    fontWeight: '400'
  }
}

export default Result
