/**
 * input: 依赖 React 和后端资源 API。
 * output: 向外提供视频、音频、字幕等资源的管理功能。
 * pos: 位于组件层，负责资源的浏览、下载和删除。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function ResourcesManager() {
  const [resourceType, setResourceType] = useState('videos') // videos, audio, manifests
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalSize: 0,
    videoCount: 0,
    audioCount: 0,
    manifestCount: 0
  })

  useEffect(() => {
    loadResources()
  }, [resourceType])

  const loadResources = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/assets/browse/${resourceType}`)
      setResources(response.data.files || [])
      setStats(response.data.stats || stats)
    } catch (error) {
      console.error('Failed to load resources:', error)
      setResources([])
    } finally {
      setLoading(false)
    }
  }

  const downloadResource = (path) => {
    window.open(`${API_BASE}${path}`, '_blank')
  }

  const deleteResource = async (path) => {
    if (!confirm('确定要删除这个资源吗？')) return

    try {
      await axios.delete(`${API_BASE}/assets/file`, {
        params: { path }
      })
      alert('资源已删除')
      loadResources()
    } catch (error) {
      console.error('Failed to delete resource:', error)
      alert('删除资源失败')
    }
  }

  const formatSize = (bytes) => {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.tabs}>
          <button
            style={{...styles.tab, ...(resourceType === 'videos' ? styles.tabActive : {})}}
            onClick={() => setResourceType('videos')}
          >
            🎬 视频 ({stats.videoCount})
          </button>
          <button
            style={{...styles.tab, ...(resourceType === 'audio' ? styles.tabActive : {})}}
            onClick={() => setResourceType('audio')}
          >
            🎵 音频 ({stats.audioCount})
          </button>
          <button
            style={{...styles.tab, ...(resourceType === 'manifests' ? styles.tabActive : {})}}
            onClick={() => setResourceType('manifests')}
          >
            📄 配置文件 ({stats.manifestCount})
          </button>
        </div>
        <div style={styles.statsBar}>
          <div style={styles.statItem}>
            总存储: <strong>{formatSize(stats.totalSize)}</strong>
          </div>
          <button onClick={loadResources} style={styles.refreshButton}>
            🔄 刷新
          </button>
        </div>
      </div>

      {loading ? (
        <div style={styles.loading}>加载中...</div>
      ) : resources.length === 0 ? (
        <div style={styles.empty}>
          <p>暂无{getResourceTypeName(resourceType)}资源</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {resources.map((resource, index) => (
            <ResourceCard
              key={index}
              resource={resource}
              type={resourceType}
              onDownload={downloadResource}
              onDelete={deleteResource}
              formatSize={formatSize}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function ResourceCard({ resource, type, onDownload, onDelete, formatSize }) {
  const getIcon = () => {
    switch (type) {
      case 'videos':
        return '🎬'
      case 'audio':
        return '🎵'
      case 'manifests':
        return '📄'
      default:
        return '📁'
    }
  }

  return (
    <div style={styles.card}>
      <div style={styles.cardIcon}>{getIcon()}</div>
      <div style={styles.cardContent}>
        <div style={styles.cardTitle} title={resource.name}>
          {resource.name}
        </div>
        <div style={styles.cardMeta}>
          <span>{formatSize(resource.size)}</span>
          <span>•</span>
          <span>{new Date(resource.modified).toLocaleDateString('zh-CN')}</span>
        </div>
        {resource.path && (
          <div style={styles.cardPath}>
            <code style={styles.code}>{resource.path}</code>
          </div>
        )}
      </div>
      <div style={styles.cardActions}>
        <button
          onClick={() => onDownload(resource.path)}
          style={styles.downloadButton}
          title="下载"
        >
          ⬇️
        </button>
        <button
          onClick={() => onDelete(resource.path)}
          style={styles.deleteButton}
          title="删除"
        >
          🗑️
        </button>
      </div>
    </div>
  )
}

function getResourceTypeName(type) {
  const names = {
    videos: '视频',
    audio: '音频',
    manifests: '配置文件'
  }
  return names[type] || ''
}

const styles = {
  container: {
    padding: '20px'
  },
  header: {
    marginBottom: '30px'
  },
  tabs: {
    display: 'flex',
    gap: '8px',
    borderBottom: '2px solid #e5e7eb',
    marginBottom: '20px'
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
  statsBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
  },
  statItem: {
    fontSize: '14px',
    color: '#6b7280'
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
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '20px'
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    display: 'flex',
    gap: '16px',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'default'
  },
  cardIcon: {
    fontSize: '32px',
    flexShrink: 0
  },
  cardContent: {
    flex: 1,
    minWidth: 0
  },
  cardTitle: {
    fontSize: '15px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '8px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap'
  },
  cardMeta: {
    fontSize: '13px',
    color: '#6b7280',
    display: 'flex',
    gap: '8px',
    marginBottom: '8px'
  },
  cardPath: {
    marginTop: '8px'
  },
  code: {
    backgroundColor: '#f3f4f6',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '11px',
    fontFamily: 'monospace',
    color: '#374151',
    wordBreak: 'break-all'
  },
  cardActions: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    flexShrink: 0
  },
  downloadButton: {
    width: '36px',
    height: '36px',
    backgroundColor: '#667eea',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background-color 0.2s'
  },
  deleteButton: {
    width: '36px',
    height: '36px',
    backgroundColor: '#ef4444',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background-color 0.2s'
  }
}

export default ResourcesManager
