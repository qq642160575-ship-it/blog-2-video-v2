import './TimelineRuler.css';

/**
 * TimelineRuler - 时间刻度尺组件
 * 显示时间刻度，帮助用户定位关键帧位置
 */
export function TimelineRuler({ duration }) {
  // 生成时间刻度标记
  const generateMarks = () => {
    const marks = [];
    const interval = duration > 30 ? 5 : duration > 10 ? 2 : 1; // 根据时长调整间隔

    for (let i = 0; i <= duration; i += interval) {
      marks.push({
        time: i,
        position: (i / duration) * 100,
      });
    }

    return marks;
  };

  const marks = generateMarks();

  return (
    <div className="timeline-ruler">
      <div className="ruler-track">
        {marks.map((mark) => (
          <div
            key={mark.time}
            className="ruler-mark"
            style={{ left: `${mark.position}%` }}
          >
            <div className="ruler-tick" />
            <div className="ruler-label">{mark.time.toFixed(1)}s</div>
          </div>
        ))}
      </div>
    </div>
  );
}
