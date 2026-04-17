/**
 * input: 依赖 Remotion 和各 composition 组件。
 * output: 向外提供视频 composition 注册入口。
 * pos: 位于模板入口层，负责登记模板。
 * 声明: 一旦我被更新，务必更新我的开头注释，以及所属文件夹的 README.md。
 */

import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {HookTitle} from './compositions/HookTitle';
import {BulletExplain} from './compositions/BulletExplain';
import {CompareProcess} from './compositions/CompareProcess';

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
      <Composition
        id="BulletExplain"
        component={BulletExplain}
        durationInFrames={210}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: 'RAG 的核心流程',
          bullets: ['检索相关资料', '筛选可信内容', '基于上下文生成答案'],
          accentColor: '#f97316',
        }}
      />
      <Composition
        id="CompareProcess"
        component={CompareProcess}
        durationInFrames={210}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          title: '普通大模型 vs RAG',
          leftTitle: '普通回答',
          rightTitle: 'RAG 回答',
          leftPoints: ['知识可能过期', '来源不可见', '更容易幻觉'],
          rightPoints: ['知识可更新', '引用可追溯', '回答更稳'],
          footerText: '核心差别：先检索，再生成。',
        }}
      />
    </>
  );
};

registerRoot(RemotionRoot);
