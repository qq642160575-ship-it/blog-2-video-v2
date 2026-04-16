import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {HookTitle} from './compositions/HookTitle';

const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HookTitle"
        component={HookTitle}
        durationInFrames={180}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: '什么是 RAG？',
          subtitle: '检索增强生成技术解析',
        }}
      />
    </>
  );
};

registerRoot(RemotionRoot);
