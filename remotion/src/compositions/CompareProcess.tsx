import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {SubtitleItem} from './BulletExplain';

export interface CompareProcessProps {
  title: string;
  leftTitle: string;
  rightTitle: string;
  leftPoints: string[];
  rightPoints: string[];
  footerText?: string;
  audioPath?: string;
  subtitles?: SubtitleItem[];
}

const Card: React.FC<{
  title: string;
  points: string[];
  frame: number;
  delay: number;
  fps: number;
  color: string;
}> = ({title, points, frame, delay, fps, color}) => {
  const reveal = spring({
    fps,
    frame: frame - delay,
    config: {
      damping: 16,
      stiffness: 100,
    },
  });

  return (
    <div
      style={{
        flex: 1,
        minHeight: '920px',
        borderRadius: '36px',
        padding: '42px 36px',
        backgroundColor: 'rgba(255, 255, 255, 0.06)',
        border: `1px solid ${color}`,
        transform: `translateY(${interpolate(reveal, [0, 1], [50, 0])}px)`,
        opacity: reveal,
      }}
    >
      <div
        style={{
          fontSize: '28px',
          textTransform: 'uppercase',
          letterSpacing: '0.08em',
          color,
          marginBottom: '22px',
        }}
      >
        {title}
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '22px',
        }}
      >
        {points.slice(0, 4).map((point, index) => (
          <div
            key={`${title}-${index}`}
            style={{
              display: 'flex',
              gap: '16px',
              fontSize: '40px',
              lineHeight: 1.3,
            }}
          >
            <span style={{color}}>0{index + 1}</span>
            <span>{point}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const CompareProcess: React.FC<CompareProcessProps> = ({
  title,
  leftTitle,
  rightTitle,
  leftPoints,
  rightPoints,
  footerText,
  audioPath,
  subtitles,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;
  const currentSubtitle = subtitles?.find(
    (sub) => currentTimeMs >= sub.start_ms && currentTimeMs < sub.end_ms
  );

  return (
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(circle at top, #1d4ed8 0%, #0f172a 32%, #020617 100%)',
        color: '#f8fafc',
        fontFamily: 'Arial, sans-serif',
        padding: '96px 64px 180px',
      }}
    >
      {audioPath && <Audio src={audioPath} />}

      <div
        style={{
          opacity: interpolate(frame, [0, fps * 0.4], [0, 1], {
            extrapolateRight: 'clamp',
          }),
        }}
      >
        <h1
          style={{
            margin: 0,
            fontSize: '76px',
            lineHeight: 1.12,
            textAlign: 'center',
          }}
        >
          {title}
        </h1>
      </div>

      <div
        style={{
          display: 'flex',
          gap: '28px',
          marginTop: '80px',
        }}
      >
        <Card
          title={leftTitle}
          points={leftPoints}
          frame={frame}
          delay={0}
          fps={fps}
          color="#f87171"
        />
        <Card
          title={rightTitle}
          points={rightPoints}
          frame={frame}
          delay={12}
          fps={fps}
          color="#22c55e"
        />
      </div>

      {footerText ? (
        <div
          style={{
            position: 'absolute',
            left: '64px',
            right: '64px',
            bottom: '120px',
            padding: '24px 28px',
            borderRadius: '24px',
            backgroundColor: 'rgba(15, 23, 42, 0.72)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            fontSize: '34px',
            lineHeight: 1.35,
            textAlign: 'center',
          }}
        >
          {footerText}
        </div>
      ) : null}

      {currentSubtitle && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            bottom: '40px',
            transform: 'translateX(-50%)',
            maxWidth: '86%',
            backgroundColor: 'rgba(2, 6, 23, 0.85)',
            borderRadius: '18px',
            padding: '14px 26px',
          }}
        >
          <p
            style={{
              margin: 0,
              fontSize: '28px',
              lineHeight: 1.45,
              textAlign: 'center',
            }}
          >
            {currentSubtitle.text}
          </p>
        </div>
      )}
    </AbsoluteFill>
  );
};
