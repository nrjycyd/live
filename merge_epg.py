#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from lxml import etree

# 可自定义 EPG 源文件路径
EPG_FILES = [
    "epg_temp/epg1.xml",
    "epg_temp/epg2.xml",
    "epg_temp/epg3.xml"
]

OUTPUT_FILE = "e.xml"

def merge_epg(files, output):
    tv = etree.Element("tv")
    seen_channels = set()
    seen_programmes = set()

    for f in files:
        if not os.path.exists(f) or os.path.getsize(f) < 1000:
            print(f"⚠️ 跳过无效文件: {f}")
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

    # 输出合并后的 XML 文件
    etree.ElementTree(tv).write(output, encoding="utf-8", xml_declaration=True)
    print(f"🎉 合并完成: {output} 共 {len(seen_channels)} 个频道, {len(seen_programmes)} 条节目")

if __name__ == "__main__":
    merge_epg(EPG_FILES, OUTPUT_FILE)
