#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import wget
from lxml import etree

# 获取 workflow 传入的源列表（用逗号分隔）
EPG_URLS = os.environ.get("EPG_SOURCES", "")
if not EPG_URLS:
    print("❌ 未配置 EPG 源，请在 workflow 中设置 EPG_SOURCES 环境变量")
    sys.exit(1)

EPG_URLS = [url.strip() for url in EPG_URLS.split(",") if url.strip()]

EPG_TEMP_DIR = "epg_temp"
OUTPUT_FILE = "e.xml"
MIN_FILE_SIZE = 1000  # 小于 1KB 的文件视为无效

def download_sources(urls, temp_dir):
    os.makedirs(temp_dir, exist_ok=True)
    local_files = []
    for i, url in enumerate(urls, start=1):
        local_file = os.path.join(temp_dir, f"epg{i}.xml")
        try:
            print(f"📥 下载 {url} -> {local_file}")
            wget.download(url, out=local_file)
            print()  # 换行
            if os.path.getsize(local_file) < MIN_FILE_SIZE:
                print(f"⚠️ 文件过小，跳过: {local_file}")
                continue
            local_files.append(local_file)
        except Exception as e:
            print(f"⚠️ 下载失败 {url}: {e}")
    if not local_files:
        print("❌ 没有有效的 EPG 源文件可用，终止运行")
        sys.exit(1)
    return local_files

def merge_epg(files, output):
    tv = etree.Element("tv")
    seen_channels = set()
    seen_programmes = set()

    for f in files:
        if not os.path.exists(f):
            continue
        print(f"✅ 读取 {f}")
        try:
            tree = etree.parse(f)
            root = tree.getroot()
        except Exception as e:
            print(f"❌ 解析失败 {f}: {e}")
            continue

        # 合并频道
        for ch in root.findall("channel"):
            cid = ch.get("id")
            if cid and cid not in seen_channels:
                seen_channels.add(cid)
                tv.append(ch)

        # 合并节目
        for prog in root.findall("programme"):
            key = (prog.get("start"), prog.get("stop"), prog.get("channel"))
            if all(key) and key not in seen_programmes:
                seen_programmes.add(key)
                tv.append(prog)

    etree.ElementTree(tv).write(output, encoding="utf-8", xml_declaration=True)
    print(f"🎉 合并完成: {output} 共 {len(seen_channels)} 个频道, {len(seen_programmes)} 条节目")

if __name__ == "__main__":
    files = download_sources(EPG_URLS, EPG_TEMP_DIR)
    merge_epg(files, OUTPUT_FILE)
