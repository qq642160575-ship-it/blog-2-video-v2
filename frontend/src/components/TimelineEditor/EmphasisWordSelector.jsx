import { useState } from 'react';
import './EmphasisWordSelector.css';

/**
 * EmphasisWordSelector - 重点词选择器组件
 * 点击词语标记为重点词，最多选择 3 个
 */
export function EmphasisWordSelector({ voiceover, emphasisWords, onEmphasisWordsChange }) {
  // 简单分词（按空格和标点）
  const words = voiceover
    ? voiceover.split(/[\s,，。.!！?？、；;]+/).filter(w => w.length > 0)
    : [];

  const toggleWord = (word) => {
    if (emphasisWords.includes(word)) {
      // 取消选中
      onEmphasisWordsChange(emphasisWords.filter(w => w !== word));
    } else if (emphasisWords.length < 3) {
      // 选中（最多 3 个）
      onEmphasisWordsChange([...emphasisWords, word]);
    } else {
      // 已达到上限，提示用户
      alert('最多只能选择 3 个重点词');
    }
  };

  return (
    <div className="emphasis-word-selector">
      <div className="selector-header">
        <div className="selector-label">
          点击选择重点词（最多 3 个）
        </div>
        <div className="selector-count">
          已选择: {emphasisWords.length} / 3
        </div>
      </div>

      <div className="words-container">
        {words.length === 0 ? (
          <div className="words-empty">暂无旁白文本</div>
        ) : (
          words.map((word, i) => (
            <span
              key={`${word}-${i}`}
              className={`word ${emphasisWords.includes(word) ? 'selected' : ''}`}
              onClick={() => toggleWord(word)}
            >
              {word}
            </span>
          ))
        )}
      </div>

      {emphasisWords.length > 0 && (
        <div className="selected-words">
          <div className="selected-label">已选择的重点词:</div>
          <div className="selected-list">
            {emphasisWords.map((word, i) => (
              <span key={i} className="selected-word">
                {word}
                <button
                  className="remove-btn"
                  onClick={() => toggleWord(word)}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
