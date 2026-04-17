import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

function CreateProject() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    source_type: 'text'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const wordCount = formData.content.length

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/projects`, formData)
      const projectId = response.data.project_id
      console.log('Project created:', response.data)

      // Navigate to generation progress page
      navigate(`/generate/${projectId}`)
    } catch (err) {
      setError(err.response?.data?.detail || '创建项目失败')
      console.error('Error creating project:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div style={styles.container} className="fade-in">
      <div style={styles.header}>
        <h1 style={styles.title}>✨ 创建视频项目</h1>
        <p style={styles.subtitle}>将您的博文转换为精美的视频内容</p>
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.formGroup}>
          <label style={styles.label}>文章标题</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            style={styles.input}
            placeholder="输入文章标题"
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>来源类型</label>
          <select
            name="source_type"
            value={formData.source_type}
            onChange={handleChange}
            style={styles.select}
          >
            <option value="text">文本</option>
            <option value="url">URL</option>
          </select>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>
            文章内容
            <span style={styles.wordCount}>
              {wordCount} 字符
            </span>
          </label>
          <textarea
            name="content"
            value={formData.content}
            onChange={handleChange}
            required
            rows={15}
            style={styles.textarea}
            placeholder="输入或粘贴文章内容..."
          />
        </div>

        {error && (
          <div style={styles.error}>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            ...styles.button,
            ...(loading ? styles.buttonDisabled : {})
          }}
        >
          {loading ? '创建中...' : '创建项目'}
        </button>
      </form>
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '900px',
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
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '16px',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.15)'
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  label: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#333',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  wordCount: {
    fontSize: '14px',
    fontWeight: 'normal',
    color: '#888',
    backgroundColor: '#f0f0f0',
    padding: '4px 12px',
    borderRadius: '12px'
  },
  input: {
    padding: '14px 16px',
    fontSize: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    outline: 'none',
    transition: 'all 0.3s',
    fontFamily: 'inherit'
  },
  select: {
    padding: '14px 16px',
    fontSize: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    outline: 'none',
    backgroundColor: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s'
  },
  textarea: {
    padding: '14px 16px',
    fontSize: '16px',
    border: '2px solid #e0e0e0',
    borderRadius: '10px',
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    lineHeight: '1.6',
    transition: 'all 0.3s'
  },
  button: {
    padding: '16px 32px',
    fontSize: '18px',
    fontWeight: '600',
    color: 'white',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    transition: 'all 0.3s',
    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
    marginTop: '10px'
  },
  buttonDisabled: {
    background: '#ccc',
    cursor: 'not-allowed',
    boxShadow: 'none'
  },
  error: {
    padding: '14px 18px',
    backgroundColor: '#fee',
    color: '#c33',
    borderRadius: '10px',
    border: '2px solid #fcc',
    fontSize: '15px'
  },
  success: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#efe',
    borderRadius: '10px',
    border: '2px solid #cfc'
  }
}

export default CreateProject
