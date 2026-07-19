"""
Video downloader for YouTube and Bilibili
Supports automatic video and subtitle download
"""
import subprocess
import json
import os
from pathlib import Path
from typing import Tuple, Optional


class VideoDownloader:
    """视频下载器，支持 YouTube 和 Bilibili"""

    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def is_youtube_url(self, url: str) -> bool:
        """检查是否是 YouTube 链接"""
        youtube_domains = ['youtube.com', 'youtu.be', 'youtube-nocookie.com']
        return any(domain in url for domain in youtube_domains)

    def is_bilibili_url(self, url: str) -> bool:
        """检查是否是 Bilibili 链接"""
        return 'bilibili.com' in url or 'b23.tv' in url

    def check_ytdlp_installed(self) -> bool:
        """检查 yt-dlp 是否已安装"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def install_ytdlp(self) -> bool:
        """安装 yt-dlp"""
        try:
            print("📦 正在安装 yt-dlp...")
            result = subprocess.run(
                ['pip', 'install', '-U', 'yt-dlp'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("✅ yt-dlp 安装成功")
                return True
            else:
                print(f"❌ yt-dlp 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 安装过程出错: {e}")
            return False

    def get_video_info(self, url: str) -> Optional[dict]:
        """获取视频信息"""
        try:
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                url
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
        except Exception as e:
            print(f"❌ 获取视频信息失败: {e}")
            return None

    def download_video_and_subtitle(
        self,
        url: str,
        video_quality: str = "best",
        subtitle_lang: str = "zh-Hans,zh-CN,zh,en"
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        下载视频和字幕

        Args:
            url: 视频链接
            video_quality: 视频质量 (best, 1080p, 720p, 480p)
            subtitle_lang: 字幕语言优先级（逗号分隔）

        Returns:
            (video_path, subtitle_path) 元组
        """
        # 检查 yt-dlp
        if not self.check_ytdlp_installed():
            print("⚠️  yt-dlp 未安装")
            if not self.install_ytdlp():
                return None, None

        # 获取视频信息
        print("📊 获取视频信息...")
        info = self.get_video_info(url)
        if not info:
            print("❌ 无法获取视频信息")
            return None, None

        video_title = info.get('title', 'video')
        # 清理文件名
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50]  # 限制长度

        print(f"📹 视频标题: {video_title}")

        # 设置输出路径
        video_output = self.output_dir / f"{safe_title}.mp4"
        subtitle_output = self.output_dir / f"{safe_title}.srt"

        # 下载视频
        print("⬇️  开始下载视频...")
        video_cmd = [
            'yt-dlp',
            '-f', f'bestvideo[height<={video_quality.replace("p", "")}]+bestaudio/best' if 'p' in video_quality else 'best',
            '--merge-output-format', 'mp4',
            '-o', str(video_output),
            url
        ]

        try:
            result = subprocess.run(
                video_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            if result.returncode != 0:
                print(f"❌ 视频下载失败: {result.stderr}")
                return None, None
            print(f"✅ 视频下载完成: {video_output}")
        except subprocess.TimeoutExpired:
            print("❌ 视频下载超时")
            return None, None
        except Exception as e:
            print(f"❌ 视频下载出错: {e}")
            return None, None

        # 下载字幕
        print("⬇️  开始下载字幕...")
        subtitle_cmd = [
            'yt-dlp',
            '--write-sub',
            '--write-auto-sub',  # 如果没有手动字幕，下载自动生成的字幕
            '--sub-lang', subtitle_lang,
            '--sub-format', 'srt',
            '--skip-download',  # 只下载字幕，不下载视频
            '--convert-subs', 'srt',  # 转换为 SRT 格式
            '-o', str(self.output_dir / safe_title),
            url
        ]

        try:
            result = subprocess.run(
                subtitle_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # 查找下载的字幕文件
            subtitle_files = list(self.output_dir.glob(f"{safe_title}*.srt"))
            if subtitle_files:
                # 如果有多个字幕文件，优先选择中文
                for sub_file in subtitle_files:
                    if any(lang in sub_file.name for lang in ['zh-Hans', 'zh-CN', 'zh']):
                        subtitle_path = sub_file
                        break
                else:
                    subtitle_path = subtitle_files[0]

                # 重命名为标准名称
                if subtitle_path != subtitle_output:
                    subtitle_path.rename(subtitle_output)

                print(f"✅ 字幕下载完成: {subtitle_output}")
                return str(video_output), str(subtitle_output)
            else:
                print("⚠️  未找到字幕文件，可能该视频没有字幕")
                print("💡 提示: 你可以使用语音识别工具生成字幕")
                return str(video_output), None

        except subprocess.TimeoutExpired:
            print("❌ 字幕下载超时")
            return str(video_output), None
        except Exception as e:
            print(f"⚠️  字幕下载出错: {e}")
            return str(video_output), None

    def download(self, url: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        """
        统一下载接口

        Args:
            url: 视频链接（YouTube 或 Bilibili）
            **kwargs: 其他参数传递给 download_video_and_subtitle

        Returns:
            (video_path, subtitle_path) 元组
        """
        if self.is_youtube_url(url):
            print("🎬 检测到 YouTube 视频")
            return self.download_video_and_subtitle(url, **kwargs)
        elif self.is_bilibili_url(url):
            print("🎬 检测到 Bilibili 视频")
            return self.download_video_and_subtitle(url, **kwargs)
        else:
            print("❌ 不支持的视频平台")
            print("💡 支持的平台: YouTube, Bilibili")
            return None, None


def main():
    """命令行测试"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python video_downloader.py <视频链接>")
        print("示例: python video_downloader.py https://www.youtube.com/watch?v=xxxxx")
        sys.exit(1)

    url = sys.argv[1]
    downloader = VideoDownloader()
    video_path, subtitle_path = downloader.download(url)

    if video_path:
        print(f"\n✅ 下载完成!")
        print(f"📹 视频: {video_path}")
        if subtitle_path:
            print(f"📝 字幕: {subtitle_path}")
        else:
            print("⚠️  字幕: 未找到")
    else:
        print("\n❌ 下载失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
