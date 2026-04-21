import { useTimelineStore } from '../../stores/timelineStore';
import { KeyframeMarker } from './KeyframeMarker';
import './KeyframeTrack.css';

/**
 * KeyframeTrack - 关键帧轨道组件
 * 显示所有关键帧，支持拖拽调整时间
 */
export function KeyframeTrack({ sceneId }) {
  const { keyframes, duration } = useTimelineStore();

  if (!duration || duration === 0) {
    return (
      <div className="keyframe-track">
        <div className="track-placeholder">等待音频加载...</div>
      </div>
    );
  }

  return (
    <div className="keyframe-track">
      <div className="track-label">关键帧</div>
      <div className="track-container">
        {keyframes.length === 0 ? (
          <div className="track-empty">暂无关键帧，请先选择重点词</div>
        ) : (
          keyframes.map((keyframe) => (
            <KeyframeMarker
              key={keyframe.id}
              keyframe={keyframe}
              duration={duration}
              sceneId={sceneId}
            />
          ))
        )}
      </div>
    </div>
  );
}
