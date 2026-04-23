/**
 * input: 依赖 Remotion 组件参数和字幕/音频 props。
 * output: 向外提供 HookTitle 视频模板。
 * pos: 位于模板层，负责开头钩子场景。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Audio, staticFile} from 'remotion';

export interface HookTitleProps {
  title: string;
  subtitle: string;
  audioPath?: string;
  subtitles?: Array<{text: string; start_ms: number; end_ms: number}>;
  timeline?: {
    keyframes?: Array<{
      time: number;
      element: string;
      action: string;
      duration: number;
    }>;
  };
}

export const HookTitle: React.FC<HookTitleProps> = ({title, subtitle, audioPath, subtitles, timeline}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Calculate current time in seconds
  const currentTimeSec = frame / fps;
  const currentTimeMs = currentTimeSec * 1000;

  // Fade in animation for title (0-0.5s)
  const titleOpacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Fade in animation for subtitle (0.3-0.8s)
  const subtitleOpacity = interpolate(frame, [fps * 0.3, fps * 0.8], [0, 1], {
    extrapolateRight: 'clamp',
  });

  // Find active keyframes for emphasis effects
  const getKeyframeEffect = (text: string) => {
    if (!timeline?.keyframes) return { scale: 1, color: '#ffffff' };

    const activeKeyframe = timeline.keyframes.find((kf) => {
      const kfStart = kf.time;
      const kfEnd = kf.time + kf.duration;
      return (
        currentTimeSec >= kfStart &&
        currentTimeSec < kfEnd &&
        text.includes(kf.element)
      );
    });

    if (activeKeyframe) {
      // Calculate progress within keyframe (0 to 1)
      const progress = (currentTimeSec - activeKeyframe.time) / activeKeyframe.duration;

      // Pop effect: scale up then down
      const scale = interpolate(progress, [0, 0.3, 1], [1, 1.2, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });

      return {
        scale,
        color: '#ffd700', // Gold color for emphasis
      };
    }

    return { scale: 1, color: '#ffffff' };
  };

  // Apply effects to title and subtitle
  const titleEffect = getKeyframeEffect(title);
  const subtitleEffect = getKeyframeEffect(subtitle);

  // Find current subtitle
  const currentSubtitle = subtitles?.find(
    (sub) => currentTimeMs >= sub.start_ms && currentTimeMs < sub.end_ms
  );

  // Convert audio path to relative path for staticFile
  const getAudioSrc = (path: string | undefined) => {
    if (!path) return undefined;
    // Remove storage prefix - staticFile expects path relative to public dir
    // e.g., "./storage/audio/file.mp3" -> "audio/file.mp3"
    const relativePath = path.replace(/^.*\/storage\//, '').replace(/^\.\/storage\//, '');
    return staticFile(relativePath);
  };

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
      {audioPath && <Audio src={getAudioSrc(audioPath)} />}

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
            color: titleEffect.color,
            margin: '0 0 30px 0',
            opacity: titleOpacity,
            lineHeight: 1.2,
            transform: `scale(${titleEffect.scale})`,
            transition: 'transform 0.1s ease-out',
          }}
        >
          {title}
        </h1>
        <p
          style={{
            fontSize: '36px',
            color: subtitleEffect.color === '#ffffff' ? '#a8dadc' : subtitleEffect.color,
            margin: 0,
            opacity: subtitleOpacity,
            lineHeight: 1.4,
            transform: `scale(${subtitleEffect.scale})`,
            transition: 'transform 0.1s ease-out',
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
