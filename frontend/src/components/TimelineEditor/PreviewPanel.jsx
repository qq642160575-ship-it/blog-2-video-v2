import { useState } from 'react';
import './PreviewPanel.css';

/**
 * PreviewPanel - 预览面板组件
 * 点击预览按钮，生成并播放预览视频
 */
export function PreviewPanel({ sceneId }) {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePreview = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:8000/scenes/${sceneId}/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('预览生成失败');
      }

      const data = await response.json();

      if (data.preview_url) {
        // 构建完整的预览 URL
        const fullUrl = `http://localhost:8000${data.preview_url}`;
        setPreviewUrl(fullUrl);
      } else {
        setError('预览生成失败，请稍后重试');
      }
    } catch (err) {
      console.error('预览生成失败', err);
      setError(err.message || '预览生成失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="preview-panel">
      <div className="panel-header">
        <div className="panel-label">预览视频</div>
        <button
          className="preview-btn"
          onClick={handlePreview}
          disabled={loading}
        >
          {loading ? '生成中...' : '🎬 生成预览'}
        </button>
      </div>

      {error && (
        <div className="preview-error">
          <div className="error-icon">⚠️</div>
          <div className="error-message">{error}</div>
          <div className="error-hint">
            提示: 预览功能需要 Remotion 渲染服务集成（阶段三 Step 7）
          </div>
        </div>
      )}

      {previewUrl && (
        <div className="preview-video-container">
          <video
            src={previewUrl}
            controls
            autoPlay
            className="preview-video"
          />
        </div>
      )}

      {!previewUrl && !error && !loading && (
        <div className="preview-placeholder">
          <div className="placeholder-icon">🎥</div>
          <div className="placeholder-text">点击"生成预览"按钮查看效果</div>
        </div>
      )}
    </div>
  );
}
