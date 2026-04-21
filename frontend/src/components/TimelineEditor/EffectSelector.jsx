import { useTimelineStore } from '../../stores/timelineStore';
import './EffectSelector.css';

/**
 * EffectSelector - 动效选择器组件
 * 显示 3 种动效选项，点击应用到选中的关键帧
 */

const EFFECTS = [
  { value: 'pop', label: 'Pop', description: '弹出效果', icon: '💥' },
  { value: 'fade_in', label: 'Fade In', description: '淡入效果', icon: '✨' },
  { value: 'slide_in', label: 'Slide In', description: '滑入效果', icon: '➡️' },
];

export function EffectSelector() {
  const { selectedKeyframeId, keyframes, updateKeyframe } = useTimelineStore();
  const selectedKeyframe = keyframes.find(kf => kf.id === selectedKeyframeId);

  if (!selectedKeyframe) {
    return (
      <div className="effect-selector">
        <div className="selector-header">
          <div className="selector-label">动效类型</div>
        </div>
        <div className="no-selection">
          请先选择一个关键帧
        </div>
      </div>
    );
  }

  const handleEffectChange = (action) => {
    updateKeyframe(selectedKeyframeId, { action });
  };

  return (
    <div className="effect-selector">
      <div className="selector-header">
        <div className="selector-label">动效类型</div>
        <div className="selected-keyframe-info">
          关键帧: {selectedKeyframe.element}
        </div>
      </div>

      <div className="effects-grid">
        {EFFECTS.map(effect => (
          <button
            key={effect.value}
            className={`effect-btn ${selectedKeyframe.action === effect.value ? 'active' : ''}`}
            onClick={() => handleEffectChange(effect.value)}
          >
            <div className="effect-icon">{effect.icon}</div>
            <div className="effect-label">{effect.label}</div>
            <div className="effect-desc">{effect.description}</div>
          </button>
        ))}
      </div>

      <div className="effect-preview">
        <div className="preview-label">当前动效:</div>
        <div className="preview-value">
          {EFFECTS.find(e => e.value === selectedKeyframe.action)?.label || 'Pop'}
        </div>
      </div>
    </div>
  );
}
