import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTimelineStore } from '../stores/timelineStore';
import { TimelineEditor } from '../components/TimelineEditor/TimelineEditor';
import { EmphasisWordSelector } from '../components/TimelineEditor/EmphasisWordSelector';
import { EffectSelector } from '../components/TimelineEditor/EffectSelector';
import { PreviewPanel } from '../components/TimelineEditor/PreviewPanel';
import './TimelineEditorPage.css';

/**
 * TimelineEditorPage - 时间轴编辑器页面
 * 整合所有编辑器组件，提供完整的编辑体验
 */
export function TimelineEditorPage() {
  const { sceneId } = useParams();
  const [scene, setScene] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const {
    setKeyframes,
    setEmphasisWords,
    emphasisWords,
    reset
  } = useTimelineStore();

  // 加载场景数据
  useEffect(() => {
    const loadScene = async () => {
      try {
        const response = await fetch(`http://localhost:8000/scenes/${sceneId}`);
        if (!response.ok) {
          throw new Error('场景加载失败');
        }

        const data = await response.json();
        setScene(data);

        // 初始化状态
        if (data.emphasis_words) {
          setEmphasisWords(data.emphasis_words);
        }

        if (data.timeline_data && data.timeline_data.keyframes) {
          // 为每个关键帧添加 id
          const keyframesWithIds = data.timeline_data.keyframes.map((kf, i) => ({
            ...kf,
            id: kf.id || `kf-${i}`,
            action: kf.action || 'pop'
          }));
          setKeyframes(keyframesWithIds);
        }

        setLoading(false);
      } catch (err) {
        console.error('加载场景失败:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    loadScene();

    return () => {
      reset();
    };
  }, [sceneId, setKeyframes, setEmphasisWords, reset]);

  // 处理重点词变化
  const handleEmphasisWordsChange = async (newWords) => {
    setEmphasisWords(newWords);

    // 保存到后端并重新计算时间轴
    try {
      const response = await fetch(`http://localhost:8000/scenes/${sceneId}/timeline`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emphasis_words: newWords })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.timeline_data && data.timeline_data.keyframes) {
          const keyframesWithIds = data.timeline_data.keyframes.map((kf, i) => ({
            ...kf,
            id: kf.id || `kf-${i}`,
            action: kf.action || 'pop'
          }));
          setKeyframes(keyframesWithIds);
        }
      }
    } catch (err) {
      console.error('保存重点词失败:', err);
    }
  };

  if (loading) {
    return (
      <div className="timeline-editor-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">加载场景数据...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="timeline-editor-page">
        <div className="error-container">
          <div className="error-icon">❌</div>
          <div className="error-title">加载失败</div>
          <div className="error-message">{error}</div>
        </div>
      </div>
    );
  }

  const audioUrl = scene.audio_url || `http://localhost:8000/storage/audio/${sceneId}.mp3`;

  return (
    <div className="timeline-editor-page">
      <div className="page-header">
        <h1 className="page-title">时间轴编辑器</h1>
        <div className="scene-info">
          <span className="scene-id">场景 ID: {sceneId}</span>
        </div>
      </div>

      <div className="editor-container">
        <div className="editor-main">
          <TimelineEditor sceneId={sceneId} audioUrl={audioUrl} />

          <EmphasisWordSelector
            voiceover={scene.voiceover}
            emphasisWords={emphasisWords}
            onEmphasisWordsChange={handleEmphasisWordsChange}
          />
        </div>

        <div className="editor-sidebar">
          <EffectSelector />
          <PreviewPanel sceneId={sceneId} />
        </div>
      </div>
    </div>
  );
}
