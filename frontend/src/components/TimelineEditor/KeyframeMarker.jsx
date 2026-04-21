import { useState, useRef } from 'react';
import { useTimelineStore } from '../../stores/timelineStore';
import { debounce } from 'lodash';
import './KeyframeMarker.css';

/**
 * KeyframeMarker - 关键帧标记组件
 * 可拖拽调整时间，点击选中
 */
export function KeyframeMarker({ keyframe, duration, sceneId }) {
  const { selectKeyframe, selectedKeyframeId, updateKeyframe } = useTimelineStore();
  const [isDragging, setIsDragging] = useState(false);
  const trackRef = useRef(null);

  const isSelected = selectedKeyframeId === keyframe.id;

  // 防抖保存到后端
  const debouncedSave = useRef(
    debounce(async (sceneId, keyframes) => {
      try {
        const response = await fetch(`http://localhost:8000/scenes/${sceneId}/timeline`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            timeline_data: { keyframes }
          })
        });

        if (!response.ok) {
          console.error('Failed to save timeline');
        }
      } catch (error) {
        console.error('Error saving timeline:', error);
      }
    }, 500)
  ).current;

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
    selectKeyframe(keyframe.id);

    const track = e.currentTarget.parentElement;
    trackRef.current = track;

    const handleMouseMove = (moveEvent) => {
      if (!trackRef.current) return;

      const rect = trackRef.current.getBoundingClientRect();
      const x = moveEvent.clientX - rect.left;
      const newTime = Math.max(0, Math.min((x / rect.width) * duration, duration));

      updateKeyframe(keyframe.id, { time: newTime });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);

      // 保存到后端
      const { keyframes } = useTimelineStore.getState();
      debouncedSave(sceneId, keyframes);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleClick = (e) => {
    if (!isDragging) {
      selectKeyframe(keyframe.id);
    }
  };

  const position = (keyframe.time / duration) * 100;

  return (
    <div
      className={`keyframe-marker ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      style={{ left: `${position}%` }}
      onMouseDown={handleMouseDown}
      onClick={handleClick}
    >
      <div className="marker-dot" />
      <div className="marker-label">{keyframe.element}</div>
      <div className="marker-time">{keyframe.time.toFixed(2)}s</div>
    </div>
  );
}
