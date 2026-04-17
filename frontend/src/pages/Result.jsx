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
      // Navigate to progress page
      navigate(`/generate/${projectId}`)
    } catch (err) {
      alert('触发重渲染失败: ' + (err.response?.data?.detail || err.message))
    }
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>加载中...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          <h2>加载失败</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} style={styles.button}>
            返回首页
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container} className="fade-in">
      <div style={styles.header}>
        <h1 style={styles.title}>🎉 视频预览</h1>
        <p style={styles.subtitle}>您的视频已生成完成</p>
      </div>

      {/* Video Player */}
      <div style={styles.videoSection}>
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

      {/* Actions */}
      <div style={styles.actions}>
        <button onClick={handleRerender} style={styles.button}>
          重新渲染
        </button>
        <button onClick={() => navigate('/')} style={styles.buttonSecondary}>
          创建新项目
        </button>
      </div>

      {/* Scenes List */}
      <div style={styles.scenesSection}>
        <h2 style={styles.sectionTitle}>场景列表 ({scenes.length})</h2>

        {scenes.length === 0 ? (
          <div style={styles.noScenes}>暂无场景</div>
        ) : (
          <div style={styles.scenesList}>
            {scenes.map((scene, index) => (
              <div key={scene.scene_id} style={styles.sceneCard}>
                <div style={styles.sceneHeader}>
                  <span style={styles.sceneNumber}>场景 {index + 1}</span>
                  <div style={styles.sceneHeaderRight}>
                    <span style={styles.sceneVersion}>v{scene.version}</span>
                    <button
                      onClick={() => navigate(`/edit-scene/${scene.scene_id}`)}
                      style={styles.editButton}
                    >
                      编辑
                    </button>
                  </div>
                </div>

                <div style={styles.sceneInfo}>
                  <div style={styles.sceneRow}>
                    <span style={styles.sceneLabel}>模板:</span>
                    <span>{scene.template_type}</span>
                  </div>
                  <div style={styles.sceneRow}>
                    <span style={styles.sceneLabel}>时长:</span>
                    <span>{scene.duration_sec}秒</span>
                  </div>
                </div>

                <div style={styles.sceneVoiceover}>
                  <div style={styles.sceneLabel}>旁白:</div>
                  <div style={styles.voiceoverText}>{scene.voiceover}</div>
                </div>

                {scene.screen_text && scene.screen_text.length > 0 && (
                  <div style={styles.sceneScreenText}>
                    <div style={styles.sceneLabel}>屏幕文本:</div>
                    <div style={styles.screenTextList}>
                      {scene.screen_text.map((text, i) => (
                        <div key={i} style={styles.screenTextItem}>
                          {text}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '1100px',
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
  loading: {
    textAlign: 'center',
    fontSize: '20px',
    color: 'white',
    padding: '80px 20px'
  },
  error: {
    textAlign: 'center',
    padding: '50px',
    backgroundColor: 'white',
    borderRadius: '16px',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)'
  },
  videoSection: {
    marginBottom: '40px',
    backgroundColor: '#000',
    borderRadius: '16px',
    overflow: 'hidden',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)'
  },
  video: {
    width: '100%',
    maxHeight: '600px',
    display: 'block'
  },
  noVideo: {
    padding: '80px 20px',
    textAlign: 'center',
    color: '#999',
    fontSize: '18px'
  },
  actions: {
    display: 'flex',
    gap: '20px',
    justifyContent: 'center',
    marginBottom: '50px'
  },
  button: {
    padding: '14px 32px',
    fontSize: '17px',
    fontWeight: '600',
    color: 'white',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'all 0.3s',
    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
  },
  buttonSecondary: {
    padding: '14px 32px',
    fontSize: '17px',
    fontWeight: '600',
    color: '#666',
    backgroundColor: 'white',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  scenesSection: {
    marginTop: '50px'
  },
  sectionTitle: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '30px',
    color: 'white',
    textAlign: 'center'
  },
  noScenes: {
    textAlign: 'center',
    padding: '50px',
    color: '#999',
    backgroundColor: 'white',
    borderRadius: '16px',
    fontSize: '16px'
  },
  scenesList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px'
  },
  sceneCard: {
    backgroundColor: 'white',
    border: 'none',
    borderRadius: '16px',
    padding: '30px',
    transition: 'all 0.3s',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)'
  },
  sceneHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    paddingBottom: '15px',
    borderBottom: '2px solid #f0f0f0'
  },
  sceneNumber: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#333'
  },
  sceneHeaderRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  sceneVersion: {
    fontSize: '14px',
    color: '#666',
    backgroundColor: '#f0f0f0',
    padding: '6px 12px',
    borderRadius: '6px',
    fontWeight: '500'
  },
  editButton: {
    padding: '8px 16px',
    fontSize: '14px',
    fontWeight: '600',
    color: 'white',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  sceneInfo: {
    display: 'flex',
    gap: '30px',
    marginBottom: '20px'
  },
  sceneRow: {
    display: 'flex',
    gap: '10px',
    fontSize: '15px'
  },
  sceneLabel: {
    fontWeight: '600',
    color: '#666'
  },
  sceneVoiceover: {
    marginBottom: '20px'
  },
  voiceoverText: {
    marginTop: '10px',
    padding: '16px',
    backgroundColor: '#f8f9fa',
    borderRadius: '10px',
    fontSize: '15px',
    lineHeight: '1.7',
    color: '#333'
  },
  sceneScreenText: {
    marginTop: '20px'
  },
  screenTextList: {
    marginTop: '10px',
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px'
  },
  screenTextItem: {
    padding: '8px 16px',
    backgroundColor: '#e3f2fd',
    borderRadius: '8px',
    fontSize: '14px',
    color: '#1976d2',
    fontWeight: '500'
  }
}

export default Result
