import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Audio, staticFile} from 'remotion';

export interface HookTitleProps {
  title: string;
  subtitle: string;
  audioPath?: string;
  subtitles?: Array<{text: string; start_ms: number; end_ms: number}>;
}

export const HookTitle: React.FC<HookTitleProps> = ({title, subtitle, audioPath, subtitles}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Fade in animation for title (0-0.5s)
  const titleOpacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Fade in animation for subtitle (0.3-0.8s)
  const subtitleOpacity = interpolate(frame, [fps * 0.3, fps * 0.8], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Calculate current time in milliseconds
  const currentTimeMs = (frame / fps) * 1000;

  // Find current subtitle
  const currentSubtitle = subtitles?.find(
    (sub) => currentTimeMs >= sub.start_ms && currentTimeMs < sub.end_ms
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#1a1a2e',
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'Arial, sans-serif',
      }}
    >
      {/* Audio */}
      {audioPath && <Audio src={audioPath} />}

      {/* Main content */}
      <div
        style={{
          textAlign: 'center',
          padding: '40px',
          maxWidth: '80%',
        }}
      >
        <h1
          style={{
            fontSize: '72px',
            fontWeight: 'bold',
            color: '#ffffff',
            margin: '0 0 30px 0',
            opacity: titleOpacity,
            lineHeight: 1.2,
          }}
        >
          {title}
        </h1>
        <p
          style={{
            fontSize: '36px',
            color: '#a8dadc',
            margin: 0,
            opacity: subtitleOpacity,
            lineHeight: 1.4,
          }}
        >
          {subtitle}
        </p>
      </div>

      {/* Subtitle overlay */}
      {currentSubtitle && (
        <div
          style={{
            position: 'absolute',
            bottom: '80px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: '12px 24px',
            borderRadius: '8px',
            maxWidth: '80%',
          }}
        >
          <p
            style={{
              fontSize: '28px',
              color: '#ffffff',
              margin: 0,
              textAlign: 'center',
              lineHeight: 1.4,
            }}
          >
            {currentSubtitle.text}
          </p>
        </div>
      )}
    </AbsoluteFill>
  );
};
