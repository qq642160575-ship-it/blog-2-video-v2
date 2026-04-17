import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

function EditScene() {
  const { sceneId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [scene, setScene] = useState(null)
  const [formData, setFormData] = useState({
    voiceover: '',
    duration_sec: 5,
    screen_text: []
  })

  useEffect(() => {
    const fetchScene = async () => {
      try {
        // Get scene from scenes list (we need project_id to get scenes)
        // For now, we'll get it from the scene_id pattern
        const projectId = sceneId.split('_')[1]

        const response = await axios.get(
          `${API_BASE_URL}/projects/${projectId}/scenes`
        )

        const sceneData = response.data.find(s => s.scene_id === sceneId)

        if (sceneData) {
          setScene(sceneData)
          setFormData({
            voiceover: sceneData.voiceover,
            duration_sec: sceneData.duration_sec,
            screen_text: sceneData.screen_text || []
          })
        } else {
          setError('场景未找到')
        }

        setLoading(false)
      } catch (err) {
        setError(err.response?.data?.detail || '加载场景失败')
        setLoading(false)
        console.error('Error fetching scene:', err)
      }
    }

    if (sceneId) {
      fetchScene()
    }
  }, [sceneId])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'duration_sec' ? parseInt(value) : value
    }))
  }

  const handleScreenTextChange = (index, value) => {
    const newScreenText = [...formData.screen_text]
    newScreenText[index] = value
    setFormData(prev => ({
      ...prev,
      screen_text: newScreenText
    }))
  }

  const addScreenText = () => {
    if (formData.screen_text.length < 3) {
      setFormData(prev => ({
        ...prev,
        screen_text: [...prev.screen_text, '']
      }))
    }
  }

  const removeScreenText = (index) => {
    setFormData(prev => ({
      ...prev,
      screen_text: prev.screen_text.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      const response = await axios.patch(
        `${API_BASE_URL}/projects/scenes/${sceneId}`,
        formData
      )

      alert('场景更新成功！')

      // Navigate back to result page
      const projectId = sceneId.split('_')[1]
      navigate(`/result/${projectId}`)
    } catch (err) {
      setError(err.response?.data?.detail || '更新场景失败')
      console.error('Error updating scene:', err)
    } finally {
      setSaving(false)
    }
  }

  const handleRerenderAfterSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)

    try {
      // First update the scene
      await axios.patch(
        `${API_BASE_URL}/projects/scenes/${sceneId}`,
        formData
      )

      // Then trigger rerender
      const projectId = sceneId.split('_')[1]
      await axios.post(`${API_BASE_URL}/projects/${projectId}/jobs/rerender`)

      // Navigate to progress page
      navigate(`/generate/${projectId}`)
    } catch (err) {
      setError(err.response?.data?.detail || '保存并重渲染失败')
      console.error('Error:', err)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>加载中...</div>
      </div>
    )
  }

  if (error && !scene) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          <h2>加载失败</h2>
          <p>{error}</p>
          <button onClick={() => navigate(-1)} style={styles.button}>
            返回
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>编辑场景</h1>

      {scene && (
        <div style={styles.sceneInfo}>
          <div>场景 ID: {scene.scene_id}</div>
          <div>版本: v{scene.version}</div>
          <div>模板: {scene.template_type}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label style={styles.label}>
            旁白文本
            <span style={styles.hint}>
              (最多 90 字符，当前: {formData.voiceover.length})
            </span>
          </label>
          <textarea
            name="voiceover"
            value={formData.voiceover}
            onChange={handleChange}
            required
            rows={4}
            maxLength={90}
            style={styles.textarea}
            placeholder="输入旁白文本..."
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>
            时长（秒）
            <span style={styles.hint}>(4-9 秒)</span>
          </label>
          <input
            type="number"
            name="duration_sec"
            value={formData.duration_sec}
            onChange={handleChange}
            required
            min={4}
            max={9}
            style={styles.input}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>
            屏幕文本
            <span style={styles.hint}>(最多 3 条，每条最多 18 字符)</span>
          </label>

          {formData.screen_text.map((text, index) => (
            <div key={index} style={styles.screenTextRow}>
              <input
                type="text"
                value={text}
                onChange={(e) => handleScreenTextChange(index, e.target.value)}
                maxLength={18}
                style={styles.input}
                placeholder={`文本 ${index + 1}`}
              />
              <button
                type="button"
                onClick={() => removeScreenText(index)}
                style={styles.removeButton}
              >
                删除
              </button>
            </div>
          ))}

          {formData.screen_text.length < 3 && (
            <button
              type="button"
              onClick={addScreenText}
              style={styles.addButton}
            >
              + 添加屏幕文本
            </button>
          )}
        </div>

        {error && (
          <div style={styles.errorBox}>
            {error}
          </div>
        )}

        <div style={styles.actions}>
          <button
            type="submit"
            disabled={saving}
            style={styles.button}
          >
            {saving ? '保存中...' : '保存'}
          </button>

          <button
            type="button"
            onClick={handleRerenderAfterSave}
            disabled={saving}
            style={styles.buttonPrimary}
          >
            {saving ? '处理中...' : '保存并重渲染'}
          </button>

          <button
            type="button"
            onClick={() => navigate(-1)}
            style={styles.buttonSecondary}
          >
            取消
          </button>
        </div>
      </form>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '40px 20px'
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333'
  },
  sceneInfo: {
    padding: '15px',
    backgroundColor: '#f5f5f5',
    borderRadius: '6px',
    marginBottom: '30px',
    fontSize: '14px',
    color: '#666',
    display: 'flex',
    gap: '20px'
  },
  loading: {
    textAlign: 'center',
    fontSize: '18px',
    color: '#666',
    padding: '60px 20px'
  },
  error: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#fee',
    borderRadius: '8px',
    border: '1px solid #fcc'
  },
  form: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  formGroup: {
    marginBottom: '25px'
  },
  label: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '16px',
    fontWeight: '600',
    color: '#555',
    marginBottom: '8px'
  },
  hint: {
    fontSize: '13px',
    fontWeight: 'normal',
    color: '#888'
  },
  input: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    outline: 'none',
    boxSizing: 'border-box'
  },
  textarea: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    boxSizing: 'border-box'
  },
  screenTextRow: {
    display: 'flex',
    gap: '10px',
    marginBottom: '10px'
  },
  removeButton: {
    padding: '12px 20px',
    fontSize: '14px',
    color: '#c33',
    backgroundColor: 'white',
    border: '1px solid #fcc',
    borderRadius: '6px',
    cursor: 'pointer',
    whiteSpace: 'nowrap'
  },
  addButton: {
    padding: '10px 16px',
    fontSize: '14px',
    color: '#007bff',
    backgroundColor: 'white',
    border: '1px solid #007bff',
    borderRadius: '6px',
    cursor: 'pointer',
    marginTop: '5px'
  },
  errorBox: {
    padding: '12px',
    backgroundColor: '#fee',
    color: '#c33',
    borderRadius: '6px',
    border: '1px solid #fcc',
    marginBottom: '20px'
  },
  actions: {
    display: 'flex',
    gap: '15px',
    justifyContent: 'flex-end'
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#28a745',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer'
  },
  buttonPrimary: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#007bff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer'
  },
  buttonSecondary: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: '#666',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '6px',
    cursor: 'pointer'
  }
}

export default EditScene
