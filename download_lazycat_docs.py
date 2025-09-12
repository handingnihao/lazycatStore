#!/usr/bin/env python3
"""
懒猫开发者文档下载器
下载 https://developer.lazycat.cloud 的所有文档并转换为Markdown格式
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import html2text
from typing import Set, List, Tuple

class LazycatDocsDownloader:
    def __init__(self, base_url: str = "https://developer.lazycat.cloud"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.visited_urls: Set[str] = set()
        self.doc_urls: List[str] = []
        self.output_dir = "lazycat_docs"
        
        # 初始化html2text转换器
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # 不限制行宽
        self.h2t.protect_links = True
        self.h2t.wrap_links = False
        self.h2t.unicode_snob = True  # 使用Unicode字符
        
    def get_all_doc_urls(self) -> List[str]:
        """获取所有文档URL"""
        print("开始收集文档URL...")
        
        # 已知的文档URL列表（基于之前的分析）
        known_urls = [
            "/index.html",
            "/start-from.html",
            "/framework.html",
            "/store-rule.html",
            "/developer-cyber-discount.html",
            "/store-submission-guide.html",
            "/wangjishanren-lazycat-developer-startup.html",
            "/develop-mode.html",
            "/lzc-cli.html",
            "/hello-world.html",
            "/app-example-python.html",
            "/app-example-python-description.html",
            "/app-example-go.html",
            "/devshell-local.html",
            "/devshell-install-and-use.html",
            "/advanced-dev-image.html",
            "/advanced-browser-extension.html",
            "/app-vnc.html",
            "/advanced-background.html",
            "/advanced-db.html",
            "/advanced-depends.html",
            "/advanced-domain.html",
            "/advanced-envs.html",
            "/advanced-error-template.html",
            "/advanced-file.html",
            "/advanced-gpu.html",
            "/advanced-l4forward.html",
            "/advanced-manifest-render.html",
            "/advanced-mime.html",
            "/advanced-multi-instance.html",
            "/advanced-oidc.html",
            "/advanced-platform.html",
            "/advanced-public-api.html",
            "/advanced-route.html",
            "/advanced-routes.html",
            "/advanced-secondary-domains.html",
            "/advanced-setupscript.html",
            "/app-block.html",
            "/app-example-porting.html",
            "/changelogs/v1.2.0.html",
            "/changelogs/v1.3.0.html",
            "/changelogs/v1.3.4.html",
            "/changelogs/v1.3.6.html",
            "/changelogs/v1.3.7.html",
            "/changelogs/v1.3.8.html",
            "/changelogs/v1.3.9.html",
            "/dockerd-support.html",
            "/extensions.html",
            "/faq-dev.html",
            "/faq-startup_script.html",
            "/http-request-headers.html",
            "/kvm.html",
            "/network-config.html",
            "/network-pass-through.html",
            "/network.html",
            "/publish-app.html",
            "/spec/build.html",
            "/spec/manifest.html",
            "/ssh.html",
        ]
        
        # 访问主页获取更多链接
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找所有链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.html') and not href.startswith('http'):
                    if href not in known_urls:
                        known_urls.append(href)
        except Exception as e:
            print(f"警告：无法从主页获取链接 - {e}")
        
        # 转换为完整URL
        self.doc_urls = [urljoin(self.base_url, url) for url in known_urls]
        print(f"找到 {len(self.doc_urls)} 个文档页面")
        return self.doc_urls
    
    def extract_main_content(self, html: str) -> str:
        """从HTML中提取主要内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # VitePress文档的主要内容通常在以下选择器中
        content_selectors = [
            '.VPDoc',  # VitePress主要内容区域
            '.vp-doc',
            '.VPContent',
            'main.main',
            'div.content',
            'article',
            'div[class*="content"]',
            'main'
        ]
        
        main_content = None
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 检查是否包含有意义的内容
                if len(element.text.strip()) > 100:  # 至少有100个字符
                    main_content = element
                    break
        
        if not main_content:
            # 如果找不到主要内容区域，尝试获取body内容
            main_content = soup.find('body')
        
        if main_content:
            # 移除导航、侧边栏等无关元素
            for element in main_content.select('nav, aside, .sidebar, .navbar, header, footer, .vp-sidebar'):
                element.decompose()
            
            return str(main_content)
        
        return html
    
    def html_to_markdown(self, html: str, url: str) -> str:
        """将HTML转换为Markdown"""
        try:
            # 提取主要内容
            main_html = self.extract_main_content(html)
            
            # 转换为Markdown
            markdown = self.h2t.handle(main_html)
            
            # 添加文档元信息
            doc_header = f"---\nsource: {url}\ndownloaded: {time.strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n"
            
            return doc_header + markdown
        except Exception as e:
            print(f"转换失败 {url}: {e}")
            return f"# 转换失败\n\n原始URL: {url}\n错误: {e}\n"
    
    def download_and_convert(self, url: str) -> Tuple[str, str]:
        """下载并转换单个页面"""
        try:
            print(f"正在下载: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 确保使用UTF-8编码
            response.encoding = 'utf-8'
            
            # 转换为Markdown
            markdown = self.html_to_markdown(response.text, url)
            
            # 生成文件名
            parsed_url = urlparse(url)
            filename = parsed_url.path.strip('/')
            if not filename:
                filename = 'index.html'
            
            # 将.html替换为.md
            if filename.endswith('.html'):
                filename = filename[:-5] + '.md'
            
            return filename, markdown
            
        except Exception as e:
            print(f"下载失败 {url}: {e}")
            return None, None
    
    def save_markdown(self, filename: str, content: str):
        """保存Markdown文件"""
        filepath = os.path.join(self.output_dir, filename)
        
        # 创建目录
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else self.output_dir, exist_ok=True)
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已保存: {filepath}")
    
    def download_all(self):
        """下载所有文档"""
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 获取所有URL
        self.get_all_doc_urls()
        
        # 下载统计
        success_count = 0
        failed_urls = []
        
        # 下载每个文档
        for i, url in enumerate(self.doc_urls, 1):
            print(f"\n进度: {i}/{len(self.doc_urls)}")
            
            filename, markdown = self.download_and_convert(url)
            
            if filename and markdown:
                self.save_markdown(filename, markdown)
                success_count += 1
                # 避免请求过快
                time.sleep(0.5)
            else:
                failed_urls.append(url)
        
        # 打印统计信息
        print(f"\n下载完成！")
        print(f"成功: {success_count}/{len(self.doc_urls)}")
        
        if failed_urls:
            print(f"\n失败的URL:")
            for url in failed_urls:
                print(f"  - {url}")
        
        # 创建索引文件
        self.create_index()
    
    def create_index(self):
        """创建文档索引"""
        index_path = os.path.join(self.output_dir, "README.md")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# 懒猫开发者文档\n\n")
            f.write(f"下载时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"源网站: {self.base_url}\n\n")
            f.write("## 文档列表\n\n")
            
            # 列出所有下载的文件
            for root, dirs, files in os.walk(self.output_dir):
                for file in sorted(files):
                    if file.endswith('.md') and file != 'README.md':
                        rel_path = os.path.relpath(os.path.join(root, file), self.output_dir)
                        f.write(f"- [{file[:-3]}]({rel_path})\n")
        
        print(f"\n索引文件已创建: {index_path}")

def main():
    print("懒猫开发者文档下载器")
    print("=" * 50)
    
    downloader = LazycatDocsDownloader()
    
    try:
        downloader.download_all()
    except KeyboardInterrupt:
        print("\n\n下载已中断")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()