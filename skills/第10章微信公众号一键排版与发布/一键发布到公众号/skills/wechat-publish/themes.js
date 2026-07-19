/**
 * 微信公众号文章主题样式
 * 所有样式都是内联格式，适配微信公众号编辑器
 */

const themes = {
  // 主题1: 简约专业 - 适合技术/深度文章
  professional: {
    name: '简约专业',
    description: '适合技术文章、深度分析',
    primaryColor: '#1a73e8',
    styles: {
      // 文章容器
      container: 'padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 16px; line-height: 1.8; color: #333;',
      // 一级标题
      h1: 'font-size: 24px; font-weight: bold; color: #1a73e8; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 2px solid #1a73e8;',
      // 二级标题
      h2: 'font-size: 20px; font-weight: bold; color: #333; margin: 25px 0 15px 0; padding-left: 12px; border-left: 4px solid #1a73e8;',
      // 三级标题
      h3: 'font-size: 18px; font-weight: bold; color: #555; margin: 20px 0 12px 0;',
      // 四级标题
      h4: 'font-size: 16px; font-weight: bold; color: #666; margin: 18px 0 10px 0;',
      // 段落
      p: 'margin: 16px 0; line-height: 1.8; color: #3f3f3f; text-align: justify;',
      // 加粗
      strong: 'font-weight: bold; color: #1a73e8;',
      // 斜体
      em: 'font-style: italic; color: #666;',
      // 行内代码
      inlineCode: 'background-color: #f5f7f9; color: #c7254e; padding: 2px 6px; border-radius: 4px; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px;',
      // 代码块
      codeBlock: 'background-color: #282c34; color: #abb2bf; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; line-height: 1.6; margin: 16px 0;',
      // 引用块
      blockquote: 'margin: 16px 0; padding: 12px 20px; background-color: #f8f9fa; border-left: 4px solid #1a73e8; color: #666; font-style: italic;',
      // 无序列表
      ul: 'margin: 16px 0; padding-left: 24px; list-style-type: disc;',
      // 有序列表
      ol: 'margin: 16px 0; padding-left: 24px; list-style-type: decimal;',
      // 列表项
      li: 'margin: 8px 0; line-height: 1.8; color: #3f3f3f;',
      // 链接
      a: 'color: #1a73e8; text-decoration: none; border-bottom: 1px solid #1a73e8;',
      // 图片
      img: 'max-width: 100%; height: auto; border-radius: 8px; margin: 16px auto; display: block; box-shadow: 0 4px 12px rgba(0,0,0,0.1);',
      // 图片说明
      figcaption: 'text-align: center; color: #999; font-size: 14px; margin-top: 8px;',
      // 分割线
      hr: 'border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;',
      // 表格
      table: 'width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px;',
      th: 'background-color: #1a73e8; color: white; padding: 12px; text-align: left; font-weight: bold;',
      td: 'padding: 10px 12px; border-bottom: 1px solid #e0e0e0;',
      trEven: 'background-color: #f8f9fa;',
    }
  },

  // 主题2: 优雅文艺 - 适合散文/随笔
  elegant: {
    name: '优雅文艺',
    description: '适合散文、随笔、生活类文章',
    primaryColor: '#2d5a27',
    styles: {
      container: 'padding: 24px; font-family: "Georgia", "Songti SC", serif; font-size: 17px; line-height: 2; color: #2c3e50;',
      h1: 'font-size: 26px; font-weight: normal; color: #2d5a27; margin: 36px 0 24px 0; text-align: center; letter-spacing: 2px;',
      h2: 'font-size: 21px; font-weight: normal; color: #2d5a27; margin: 30px 0 18px 0; text-align: center; letter-spacing: 1px;',
      h3: 'font-size: 18px; font-weight: bold; color: #34495e; margin: 24px 0 14px 0;',
      h4: 'font-size: 16px; font-weight: normal; color: #5d6d7e; margin: 20px 0 12px 0;',
      p: 'margin: 20px 0; line-height: 2; color: #34495e; text-indent: 2em; text-align: justify;',
      strong: 'font-weight: bold; color: #2d5a27;',
      em: 'font-style: italic; color: #7f8c8d;',
      inlineCode: 'background-color: #ecf0f1; color: #2d5a27; padding: 2px 6px; border-radius: 3px; font-family: "SFMono-Regular", Consolas, monospace; font-size: 15px;',
      codeBlock: 'background-color: #2c3e50; color: #ecf0f1; padding: 18px; border-radius: 6px; overflow-x: auto; font-family: "SFMono-Regular", Consolas, monospace; font-size: 14px; line-height: 1.7; margin: 20px 0;',
      blockquote: 'margin: 24px 0; padding: 16px 24px; background-color: #f9f9f7; border-left: 3px solid #2d5a27; color: #5d6d7e; font-style: italic; line-height: 1.9;',
      ul: 'margin: 18px 0; padding-left: 28px; list-style-type: disc;',
      ol: 'margin: 18px 0; padding-left: 28px; list-style-type: decimal;',
      li: 'margin: 10px 0; line-height: 1.9; color: #34495e;',
      a: 'color: #2d5a27; text-decoration: none; border-bottom: 1px dashed #2d5a27;',
      img: 'max-width: 100%; height: auto; border-radius: 4px; margin: 24px auto; display: block;',
      figcaption: 'text-align: center; color: #95a5a6; font-size: 14px; margin-top: 10px; font-style: italic;',
      hr: 'border: none; height: 20px; margin: 36px 0; background: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 10\'%3E%3Ctext x=\'50\' y=\'8\' text-anchor=\'middle\' fill=\'%232d5a27\' font-size=\'10\'%3E%E2%9C%A6%3C/text%3E%3C/svg%3E") center no-repeat;',
      table: 'width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 15px;',
      th: 'background-color: #2d5a27; color: white; padding: 14px; text-align: left;',
      td: 'padding: 12px 14px; border-bottom: 1px solid #e0e0e0;',
      trEven: 'background-color: #f9f9f7;',
    }
  },

  // 主题3: 活力橙 - 适合营销/公告
  vibrant: {
    name: '活力橙',
    description: '适合营销、公告、活动类文章',
    primaryColor: '#ff6b35',
    styles: {
      container: 'padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.8; color: #333;',
      h1: 'font-size: 26px; font-weight: bold; color: #ff6b35; margin: 28px 0 18px 0; text-align: center; padding: 10px 0; background: linear-gradient(90deg, #fff5f0 0%, #fff 50%, #fff5f0 100%);',
      h2: 'font-size: 20px; font-weight: bold; color: #ff6b35; margin: 24px 0 14px 0; padding: 8px 16px; background-color: #fff5f0; border-radius: 6px;',
      h3: 'font-size: 18px; font-weight: bold; color: #e55a2b; margin: 20px 0 12px 0;',
      h4: 'font-size: 16px; font-weight: bold; color: #ff6b35; margin: 18px 0 10px 0;',
      p: 'margin: 16px 0; line-height: 1.85; color: #444;',
      strong: 'font-weight: bold; color: #ff6b35;',
      em: 'font-style: italic; color: #888;',
      inlineCode: 'background-color: #fff5f0; color: #ff6b35; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 14px;',
      codeBlock: 'background-color: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; overflow-x: auto; font-family: monospace; font-size: 14px; line-height: 1.6; margin: 16px 0; border-left: 4px solid #ff6b35;',
      blockquote: 'margin: 18px 0; padding: 14px 20px; background-color: #fff5f0; border-left: 4px solid #ff6b35; color: #666; border-radius: 0 8px 8px 0;',
      ul: 'margin: 16px 0; padding-left: 24px; list-style-type: disc;',
      ol: 'margin: 16px 0; padding-left: 24px; list-style-type: decimal;',
      li: 'margin: 8px 0; line-height: 1.8; color: #444;',
      a: 'color: #ff6b35; text-decoration: none; font-weight: bold;',
      img: 'max-width: 100%; height: auto; border-radius: 12px; margin: 20px auto; display: block; box-shadow: 0 6px 20px rgba(255,107,53,0.15);',
      figcaption: 'text-align: center; color: #999; font-size: 14px; margin-top: 10px;',
      hr: 'border: none; border-top: 2px dashed #ff6b35; margin: 28px 0;',
      table: 'width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; border-radius: 8px; overflow: hidden;',
      th: 'background-color: #ff6b35; color: white; padding: 12px; text-align: left; font-weight: bold;',
      td: 'padding: 10px 12px; border-bottom: 1px solid #ffe0d0;',
      trEven: 'background-color: #fff5f0;',
    }
  },

  // 主题4: 暗黑极客 - 适合程序员向内容
  dark: {
    name: '暗黑极客',
    description: '适合程序员向、技术极客类内容',
    primaryColor: '#61dafb',
    styles: {
      container: 'padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; line-height: 1.8; color: #e0e0e0; background-color: #1a1a2e;',
      h1: 'font-size: 24px; font-weight: bold; color: #61dafb; margin: 28px 0 18px 0; padding-bottom: 10px; border-bottom: 2px solid #61dafb;',
      h2: 'font-size: 20px; font-weight: bold; color: #bb86fc; margin: 24px 0 14px 0; padding-left: 14px; border-left: 4px solid #bb86fc;',
      h3: 'font-size: 18px; font-weight: bold; color: #03dac6; margin: 20px 0 12px 0;',
      h4: 'font-size: 16px; font-weight: bold; color: #bb86fc; margin: 18px 0 10px 0;',
      p: 'margin: 16px 0; line-height: 1.85; color: #b0b0b0;',
      strong: 'font-weight: bold; color: #61dafb;',
      em: 'font-style: italic; color: #888;',
      inlineCode: 'background-color: #2d2d44; color: #f8c555; padding: 2px 8px; border-radius: 4px; font-family: "Fira Code", "SFMono-Regular", Consolas, monospace; font-size: 14px;',
      codeBlock: 'background-color: #0d1117; color: #c9d1d9; padding: 18px; border-radius: 8px; overflow-x: auto; font-family: "Fira Code", "SFMono-Regular", Consolas, monospace; font-size: 14px; line-height: 1.6; margin: 18px 0; border: 1px solid #30363d;',
      blockquote: 'margin: 18px 0; padding: 14px 20px; background-color: #2d2d44; border-left: 4px solid #61dafb; color: #a0a0a0;',
      ul: 'margin: 16px 0; padding-left: 24px; list-style-type: disc;',
      ol: 'margin: 16px 0; padding-left: 24px; list-style-type: decimal;',
      li: 'margin: 8px 0; line-height: 1.8; color: #b0b0b0;',
      a: 'color: #61dafb; text-decoration: none; border-bottom: 1px solid #61dafb;',
      img: 'max-width: 100%; height: auto; border-radius: 8px; margin: 20px auto; display: block; border: 1px solid #30363d;',
      figcaption: 'text-align: center; color: #666; font-size: 14px; margin-top: 10px;',
      hr: 'border: none; border-top: 1px solid #30363d; margin: 28px 0;',
      table: 'width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px;',
      th: 'background-color: #2d2d44; color: #61dafb; padding: 12px; text-align: left; font-weight: bold; border-bottom: 2px solid #61dafb;',
      td: 'padding: 10px 12px; border-bottom: 1px solid #30363d; color: #b0b0b0;',
      trEven: 'background-color: #16162a;',
    }
  }
};

module.exports = themes;
