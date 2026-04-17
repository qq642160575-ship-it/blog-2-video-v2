/**
 * input: 依赖 Remotion 组件参数和字幕/音频 props。
 * output: 向外提供 BulletExplain 视频模板。
 * pos: 位于模板层，负责要点解释场景。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export interface SubtitleItem {
  text: string;
  start_ms: number;
  end_ms: number;
}

export interface BulletExplainProps {
  title: string;
  bullets: string[];
  accentColor?: string;
  audioPath?: string;
  subtitles?: SubtitleItem[];
}

export const BulletExplain: React.FC<BulletExplainProps> = ({
  title,
  bullets,
  accentColor = '#f97316',
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
          'linear-gradient(180deg, #0f172a 0%, #111827 48%, #1e293b 100%)',
        color: '#f8fafc',
        fontFamily: 'Arial, sans-serif',
        padding: '120px 80px 180px',
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
        <div
          style={{
            display: 'inline-block',
            padding: '10px 18px',
            borderRadius: '999px',
            backgroundColor: 'rgba(249, 115, 22, 0.15)',
            color: accentColor,
            fontSize: '26px',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: '28px',
          }}
        >
          Key Points
        </div>

        <h1
          style={{
            fontSize: '78px',
            lineHeight: 1.1,
            margin: 0,
            maxWidth: '860px',
          }}
        >
          {title}
        </h1>
      </div>

      <div
        style={{
          marginTop: '90px',
          display: 'flex',
          flexDirection: 'column',
          gap: '28px',
        }}
      >
        {bullets.slice(0, 4).map((bullet, index) => {
          const entrance = spring({
            fps,
            frame: frame - index * 10,
            config: {
              damping: 18,
              stiffness: 110,
            },
          });

          return (
            <div
              key={`${bullet}-${index}`}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '24px',
                padding: '28px 32px',
                borderRadius: '28px',
                backgroundColor: 'rgba(15, 23, 42, 0.7)',
                border: '1px solid rgba(148, 163, 184, 0.18)',
                transform: `translateY(${interpolate(
                  entrance,
                  [0, 1],
                  [40, 0]
                )}px)`,
                opacity: entrance,
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '999px',
                  backgroundColor: accentColor,
                  marginTop: '14px',
                  flexShrink: 0,
                  boxShadow: `0 0 24px ${accentColor}`,
                }}
              />
              <div
                style={{
                  fontSize: '46px',
                  lineHeight: 1.3,
                  fontWeight: 600,
                }}
              >
                {bullet}
              </div>
            </div>
          );
        })}
      </div>

      {currentSubtitle && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            bottom: '72px',
            transform: 'translateX(-50%)',
            maxWidth: '86%',
            backgroundColor: 'rgba(2, 6, 23, 0.82)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '18px',
            padding: '16px 28px',
          }}
        >
          <p
            style={{
              margin: 0,
              fontSize: '30px',
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
