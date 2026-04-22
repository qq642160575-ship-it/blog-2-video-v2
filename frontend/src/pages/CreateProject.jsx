/**
 * Editorial Studio - Create Project Page
 * 优雅的项目创建界面，杂志编辑室美学
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function CreateProject() {
  const navigate = useNavigate()
  const [articleContent, setArticleContent] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [charCount, setCharCount] = useState(0)
  const [focused, setFocused] = useState(false)

  const handleContentChange = (e) => {
    const content = e.target.value
    setArticleContent(content)
    setCharCount(content.length)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!articleContent.trim()) {
      alert('请输入博文内容')
      return
    }

    try {
      setLoading(true)
      const response = await axios.post(`${API_BASE}/projects`, {
        title: title || '未命名项目',
        content: articleContent,
        source_type: 'text'
      })

      const projectId = response.data.project_id
      navigate(`/generate/${projectId}`)
    } catch (error) {
      console.error('Failed to create project:', error)
      alert('创建项目失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.container}>
      {/* Hero Section */}
      <div style={styles.hero}>
        <div style={styles.heroNumber}>01</div>
        <h1 style={styles.heroTitle}>
          Transform Your Words
          <br />
          Into Visual Stories
        </h1>
        <p style={styles.heroSubtitle}>
          将博文转化为精美视频，让内容更具表现力
        </p>
      </div>

      {/* Main Form */}
      <form onSubmit={handleSubmit} style={styles.form}>
        {/* Title Input */}
        <div style={styles.inputGroup}>
          <label style={styles.label}>
            <span style={styles.labelNumber}>1.1</span>
            <span style={styles.labelText}>项目标题</span>
            <span style={styles.labelOptional}>Optional</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="为你的项目命名..."
            style={styles.titleInput}
            disabled={loading}
          />
        </div>

        {/* Content Textarea */}
        <div style={styles.inputGroup}>
          <label style={styles.label}>
            <span style={styles.labelNumber}>1.2</span>
            <span style={styles.labelText}>博文内容</span>
            <span style={styles.labelRequired}>Required</span>
          </label>
          <div style={{
            ...styles.textareaWrapper,
            borderColor: focused ? '#D4A574' : '#E8E6E0',
            boxShadow: focused ? '0 0 0 3px rgba(212, 165, 116, 0.1)' : 'none'
          }}>
            <textarea
              value={articleContent}
              onChange={handleContentChange}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="粘贴或输入你的博文内容...&#10;&#10;支持多段落文本，AI 将自动分析内容结构并生成相应的视频场景。"
              style={styles.textarea}
              disabled={loading}
            />
            <div style={styles.textareaFooter}>
              <span style={styles.charCount}>
                {charCount.toLocaleString()} 字符
              </span>
              <span style={styles.hint}>
                建议 500-3000 字
              </span>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div style={styles.submitSection}>
          <button
            type="submit"
            disabled={loading || !articleContent.trim()}
            style={{
              ...styles.submitButton,
              opacity: loading || !articleContent.trim() ? 0.5 : 1,
              cursor: loading || !articleContent.trim() ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? (
              <>
                <span style={styles.spinner}>◌</span>
                <span>AI 正在处理...</span>
              </>
            ) : (
              <>
                <span>开始创作</span>
                <span style={styles.arrow}>→</span>
              </>
            )}
          </button>
          <p style={styles.submitHint}>
            点击后，AI 将分析你的内容并开始生成视频
          </p>
        </div>
      </form>

      {/* Features Grid */}
      <div style={styles.features}>
        <div style={styles.featureCard}>
          <div style={styles.featureIcon}>🎬</div>
          <h3 style={styles.featureTitle}>智能场景生成</h3>
          <p style={styles.featureText}>
            AI 自动分析文章结构，生成匹配的视频场景
          </p>
        </div>
        <div style={styles.featureCard}>
          <div style={styles.featureIcon}>🎨</div>
          <h3 style={styles.featureTitle}>专业视觉设计</h3>
          <p style={styles.featureText}>
            精美的模板和动画效果，无需设计经验
          </p>
        </div>
        <div style={styles.featureCard}>
          <div style={styles.featureIcon}>⚡</div>
          <h3 style={styles.featureTitle}>快速渲染</h3>
          <p style={styles.featureText}>
            高效的处理流程，几分钟内完成视频生成
          </p>
        </div>
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
    marginBottom: '80px',
    position: 'relative'
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
    fontWeight: '400',
    maxWidth: '600px'
  },

  // Form
  form: {
    marginBottom: '100px'
  },
  inputGroup: {
    marginBottom: '48px'
  },
  label: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '12px',
    marginBottom: '16px'
  },
  labelNumber: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#D4A574',
    fontFamily: 'Georgia, serif'
  },
  labelText: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#2C2416',
    letterSpacing: '0.01em'
  },
  labelOptional: {
    fontSize: '13px',
    color: '#9B9388',
    fontStyle: 'italic',
    marginLeft: 'auto'
  },
  labelRequired: {
    fontSize: '13px',
    color: '#D4A574',
    fontWeight: '600',
    marginLeft: 'auto'
  },

  // Title Input
  titleInput: {
    width: '100%',
    padding: '16px 20px',
    fontSize: '18px',
    fontFamily: 'inherit',
    color: '#2C2416',
    backgroundColor: '#FFFFFF',
    border: '2px solid #E8E6E0',
    borderRadius: '12px',
    outline: 'none',
    transition: 'all 0.3s ease',
    boxSizing: 'border-box'
  },

  // Textarea
  textareaWrapper: {
    backgroundColor: '#FFFFFF',
    border: '2px solid #E8E6E0',
    borderRadius: '12px',
    transition: 'all 0.3s ease',
    overflow: 'hidden'
  },
  textarea: {
    width: '100%',
    minHeight: '320px',
    padding: '24px',
    fontSize: '16px',
    fontFamily: 'inherit',
    color: '#2C2416',
    backgroundColor: 'transparent',
    border: 'none',
    outline: 'none',
    resize: 'vertical',
    lineHeight: 1.8,
    boxSizing: 'border-box'
  },
  textareaFooter: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px 24px',
    backgroundColor: '#FAF9F6',
    borderTop: '1px solid #E8E6E0'
  },
  charCount: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#2C2416'
  },
  hint: {
    fontSize: '13px',
    color: '#9B9388'
  },

  // Submit Section
  submitSection: {
    marginTop: '60px',
    textAlign: 'center'
  },
  submitButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '12px',
    padding: '20px 48px',
    fontSize: '18px',
    fontWeight: '600',
    color: '#FFFFFF',
    backgroundColor: '#2C2416',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 16px rgba(44, 36, 22, 0.2)',
    letterSpacing: '0.01em'
  },
  spinner: {
    display: 'inline-block',
    animation: 'spin 1s linear infinite',
    fontSize: '20px'
  },
  arrow: {
    fontSize: '20px',
    transition: 'transform 0.3s ease'
  },
  submitHint: {
    marginTop: '16px',
    fontSize: '14px',
    color: '#9B9388',
    fontStyle: 'italic'
  },

  // Features
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '32px',
    paddingTop: '60px',
    borderTop: '1px solid #E8E6E0'
  },
  featureCard: {
    textAlign: 'center'
  },
  featureIcon: {
    fontSize: '48px',
    marginBottom: '20px'
  },
  featureTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#2C2416',
    marginBottom: '12px',
    fontFamily: 'Georgia, serif'
  },
  featureText: {
    fontSize: '14px',
    color: '#6B6456',
    lineHeight: 1.6
  }
}

// Add keyframe animation
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style')
  styleSheet.textContent = `
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }

    button:hover .arrow {
      transform: translateX(4px);
    }

    input:focus, textarea:focus {
      border-color: #D4A574 !important;
    }
  `
  document.head.appendChild(styleSheet)
}

export default CreateProject
