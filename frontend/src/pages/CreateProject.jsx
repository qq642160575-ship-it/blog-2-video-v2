/**
 * input: 依赖 React 状态、路由跳转和项目创建 API。
 * output: 向外提供项目创建页面。
 * pos: 位于前端页面层，负责文章输入入口。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

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
    fontSize: '52px', // Section Heading
    fontWeight: '500',
    fontFamily: 'Georgia, serif', // Anthropic Serif fallback
    marginBottom: '12px',
    color: '#141413', // Near Black
    lineHeight: '1.2'
  },
  subtitle: {
    fontSize: '20px', // Body Large
    color: '#5e5d59', // Olive Gray
    margin: 0,
    lineHeight: '1.6'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    backgroundColor: '#faf9f5', // Ivory
    padding: '40px',
    borderRadius: '16px', // Very rounded
    border: '1px solid #f0eee6', // Border Cream
    boxShadow: 'rgba(0, 0, 0, 0.05) 0px 4px 24px' // Whisper shadow
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px'
  },
  label: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#141413', // Near Black
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  wordCount: {
    fontSize: '14px',
    fontWeight: 'normal',
    color: '#87867f', // Stone Gray
    backgroundColor: '#e8e6dc', // Warm Sand
    padding: '4px 12px',
    borderRadius: '12px'
  },
  input: {
    padding: '12px 16px',
    fontSize: '16px',
    border: '1px solid #f0eee6', // Border Cream
    borderRadius: '12px', // Generous
    outline: 'none',
    transition: 'all 0.2s',
    fontFamily: 'inherit',
    backgroundColor: '#ffffff',
    color: '#141413' // Near Black
  },
  select: {
    padding: '12px 16px',
    fontSize: '16px',
    border: '1px solid #f0eee6', // Border Cream
    borderRadius: '12px', // Generous
    outline: 'none',
    backgroundColor: '#ffffff',
    cursor: 'pointer',
    transition: 'all 0.2s',
    color: '#141413' // Near Black
  },
  textarea: {
    padding: '12px 16px',
    fontSize: '16px',
    border: '1px solid #f0eee6', // Border Cream
    borderRadius: '12px', // Generous
    outline: 'none',
    resize: 'vertical',
    fontFamily: 'inherit',
    lineHeight: '1.6',
    transition: 'all 0.2s',
    backgroundColor: '#ffffff',
    color: '#141413' // Near Black
  },
  button: {
    padding: '16px 32px',
    fontSize: '18px',
    fontWeight: '500',
    color: '#faf9f5', // Ivory
    backgroundColor: '#c96442', // Terracotta Brand
    border: 'none',
    borderRadius: '12px', // Generous
    cursor: 'pointer',
    transition: 'all 0.2s',
    boxShadow: '0px 0px 0px 1px #c96442', // Ring shadow
    marginTop: '10px',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif'
  },
  buttonDisabled: {
    backgroundColor: '#87867f', // Stone Gray
    cursor: 'not-allowed',
    boxShadow: 'none'
  },
  error: {
    padding: '14px 18px',
    backgroundColor: '#fee2e2',
    color: '#b53333', // Error Crimson
    borderRadius: '12px',
    border: '1px solid #b53333',
    fontSize: '15px'
  },
  success: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#d1fae5',
    borderRadius: '12px',
    border: '1px solid #10b981'
  }
}

export default CreateProject
