import { useRef, useEffect } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { useTimelineStore } from '../../stores/timelineStore';
import { TimelineRuler } from './TimelineRuler';
import { KeyframeTrack } from './KeyframeTrack';
import { getCachedWaveform, cacheWaveform } from '../../utils/waveformCache';
import './TimelineEditor.css';

/**
 * TimelineEditor - 时间轴编辑器主组件
 * 包含音频波形、时间刻度尺、关键帧轨道
 */
export function TimelineEditor({ sceneId, audioUrl }) {
  const waveformRef = useRef(null);
  const wavesurfer = useRef(null);

  const {
    setCurrentTime,
    setPlaying,
    isPlaying,
    duration,
    setDuration
  } = useTimelineStore();

  // 初始化音频波形
  useEffect(() => {
    if (waveformRef.current && audioUrl) {
      const initWaveform = async () => {
        wavesurfer.current = WaveSurfer.create({
          container: waveformRef.current,
          waveColor: '#ddd',
          progressColor: '#3b82f6',
          cursorColor: '#3b82f6',
          height: 80,
          cursorWidth: 2,
          barWidth: 2,
          barGap: 1,
          responsive: true,
          normalize: true,
        });

        // Try to load from cache first
        const cachedData = await getCachedWaveform(audioUrl);

        if (cachedData) {
          // Load from cache
          wavesurfer.current.load(audioUrl, cachedData);
        } else {
          // Load from URL and cache
          wavesurfer.current.load(audioUrl);
        }

        // Monitor loading completion
        wavesurfer.current.on('ready', async () => {
          const audioDuration = wavesurfer.current.getDuration();
          setDuration(audioDuration);
          console.log('Audio loaded, duration:', audioDuration);

          // Cache waveform data if not cached
          if (!cachedData) {
            try {
              const peaks = wavesurfer.current.exportPeaks();
              await cacheWaveform(audioUrl, peaks);
            } catch (error) {
              console.error('Failed to cache waveform:', error);
            }
          }
        });

        // Monitor playback progress
        wavesurfer.current.on('audioprocess', (time) => {
          setCurrentTime(time);
        });

        // Monitor play/pause
        wavesurfer.current.on('play', () => {
          setPlaying(true);
        });

        wavesurfer.current.on('pause', () => {
          setPlaying(false);
        });

        wavesurfer.current.on('finish', () => {
          setPlaying(false);
        });
      };

      initWaveform();
    }

    return () => {
      if (wavesurfer.current) {
        wavesurfer.current.destroy();
      }
    };
  }, [audioUrl, setCurrentTime, setPlaying, setDuration]);

  // 控制播放/暂停
  useEffect(() => {
    if (wavesurfer.current) {
      if (isPlaying) {
        wavesurfer.current.play();
      } else {
        wavesurfer.current.pause();
      }
    }
  }, [isPlaying]);

  const handlePlayPause = () => {
    setPlaying(!isPlaying);
  };

  return (
    <div className="timeline-editor">
      <div className="timeline-controls">
        <button
          className="play-pause-btn"
          onClick={handlePlayPause}
        >
          {isPlaying ? '⏸ 暂停' : '▶ 播放'}
        </button>
        <span className="duration-display">
          时长: {duration.toFixed(2)}s
        </span>
      </div>

      <div className="waveform-container" ref={waveformRef} />

      <TimelineRuler duration={duration} />

      <KeyframeTrack sceneId={sceneId} />
    </div>
  );
}
