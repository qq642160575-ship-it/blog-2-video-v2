import { create } from 'zustand';

/**
 * Timeline Editor State Management
 * 管理时间轴编辑器的状态：关键帧、选中状态、播放状态等
 */

export const useTimelineStore = create((set) => ({
  // 关键帧列表
  keyframes: [],

  // 选中的关键帧 ID
  selectedKeyframeId: null,

  // 播放状态
  isPlaying: false,

  // 当前播放时间（秒）
  currentTime: 0,

  // 场景总时长（秒）
  duration: 0,

  // 重点词列表
  emphasisWords: [],

  // Actions

  /**
   * 设置关键帧列表
   */
  setKeyframes: (keyframes) => set({ keyframes }),

  /**
   * 更新单个关键帧
   */
  updateKeyframe: (id, updates) =>
    set((state) => ({
      keyframes: state.keyframes.map((kf) =>
        kf.id === id ? { ...kf, ...updates } : kf
      ),
    })),

  /**
   * 添加关键帧
   */
  addKeyframe: (keyframe) =>
    set((state) => ({
      keyframes: [...state.keyframes, keyframe],
    })),

  /**
   * 删除关键帧
   */
  removeKeyframe: (id) =>
    set((state) => ({
      keyframes: state.keyframes.filter((kf) => kf.id !== id),
      selectedKeyframeId: state.selectedKeyframeId === id ? null : state.selectedKeyframeId,
    })),

  /**
   * 选中关键帧
   */
  selectKeyframe: (id) => set({ selectedKeyframeId: id }),

  /**
   * 设置播放状态
   */
  setPlaying: (playing) => set({ isPlaying: playing }),

  /**
   * 设置当前播放时间
   */
  setCurrentTime: (time) => set({ currentTime: time }),

  /**
   * 设置场景总时长
   */
  setDuration: (duration) => set({ duration }),

  /**
   * 设置重点词列表
   */
  setEmphasisWords: (words) => set({ emphasisWords: words }),

  /**
   * 重置所有状态
   */
  reset: () => set({
    keyframes: [],
    selectedKeyframeId: null,
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    emphasisWords: [],
  }),
}));
