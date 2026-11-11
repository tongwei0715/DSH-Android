#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问问Ai (wenwenai.cn) — 针对 jackwener/DSH-Android 的幂等品牌重塑与更新源绑定脚本
支持在拉取上游任何新版本（如 v0.3.9 / v0.3.11 / v0.4.x）后一键执行：
  python3 scripts/rebrand_wenwenai.py --github-repo tongwei0715/DSH-Android --domain wenwenai.cn
"""
import argparse
import re
import shutil
from pathlib import Path

# 108dp Adaptive Icon 前景（将 120x120 的问问Ai SVG 气泡居中置于 108x108 安全区内：缩放 0.65，平移 19.5）
IC_LAUNCHER_FG_XML = """<!-- 问问Ai (wenwenai.cn) adaptive-icon foreground centered in 66dp safe zone -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <group android:translateX="19.5" android:translateY="19.5" android:scaleX="0.575" android:scaleY="0.575">
        <path android:fillColor="#FFC93C" android:pathData="M26,62h14L24,78z"/>
        <path android:fillColor="#FFC93C" android:pathData="M34,20h26a16,16 0 0,1 16,16v14a16,16 0 0,1 -16,16h-26a16,16 0 0,1 -16,-16v-14a16,16 0 0,1 16,-16z"/>
        <path android:fillColor="#FFFFFF" android:pathData="M72,90h20l2,16z"/>
        <path android:fillColor="#FFFFFF" android:pathData="M57,44h28a17,17 0 0,1 17,17v14a17,17 0 0,1 -17,17h-28a17,17 0 0,1 -17,-17v-14a17,17 0 0,1 17,-17z"/>
        <path android:strokeColor="#2F5BFF" android:strokeWidth="5" android:strokeLineCap="round" android:pathData="M62,62c0,-8 18,-8 18,1c0,7 -9,7 -9,14"/>
        <path android:fillColor="#2F5BFF" android:pathData="M71,85m-3.2,0a3.2,3.2 0 1,1 6.4,0a3.2,3.2 0 1,1 -6.4,0"/>
        <path android:fillColor="#14213D" android:pathData="M85,12h14a11,11 0 0,1 11,11v0a11,11 0 0,1 -11,11h-14a11,11 0 0,1 -11,-11v0a11,11 0 0,1 11,-11z"/>
        <path android:strokeColor="#FFC93C" android:strokeWidth="2.6" android:strokeLineCap="round" android:pathData="M88.5,23.2m-4.2,0a4.2,4.2 0 1,1 8.4,0a4.2,4.2 0 1,1 -8.4,0"/>
        <path android:strokeColor="#FFC93C" android:strokeWidth="2.6" android:strokeLineCap="round" android:pathData="M92.7,18.4v9.6M99.5,18.4v9.6"/>
        <path android:fillColor="#FFC93C" android:pathData="M99.5,14.8m-1.6,0a1.6,1.6 0 1,1 3.2,0a1.6,1.6 0 1,1 -3.2,0"/>
    </group>
</vector>
"""

# App 内部全彩品牌 Logo (用于首页 Hero、引导页、侧边栏、关于页)
DSW_WHALE_XML = """<!-- 问问Ai (wenwenai.cn) full-color vector mark -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="120"
    android:viewportHeight="120">
    <path android:fillColor="#2F5BFF" android:pathData="M28,0h64a28,28 0 0,1 28,28v64a28,28 0 0,1 -28,28h-64a28,28 0 0,1 -28,-28v-64a28,28 0 0,1 28,-28z"/>
    <path android:fillColor="#FFC93C" android:pathData="M26,62h14L24,78z"/>
    <path android:fillColor="#FFC93C" android:pathData="M34,20h26a16,16 0 0,1 16,16v14a16,16 0 0,1 -16,16h-26a16,16 0 0,1 -16,-16v-14a16,16 0 0,1 16,-16z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M72,90h20l2,16z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M57,44h28a17,17 0 0,1 17,17v14a17,17 0 0,1 -17,17h-28a17,17 0 0,1 -17,-17v-14a17,17 0 0,1 17,-17z"/>
    <path android:strokeColor="#2F5BFF" android:strokeWidth="5" android:strokeLineCap="round" android:pathData="M62,62c0,-8 18,-8 18,1c0,7 -9,7 -9,14"/>
    <path android:fillColor="#2F5BFF" android:pathData="M71,85m-3.2,0a3.2,3.2 0 1,1 6.4,0a3.2,3.2 0 1,1 -6.4,0"/>
    <path android:fillColor="#14213D" android:pathData="M85,12h14a11,11 0 0,1 11,11v0a11,11 0 0,1 -11,11h-14a11,11 0 0,1 -11,-11v0a11,11 0 0,1 11,-11z"/>
    <path android:strokeColor="#FFC93C" android:strokeWidth="2.6" android:strokeLineCap="round" android:pathData="M88.5,23.2m-4.2,0a4.2,4.2 0 1,1 8.4,0a4.2,4.2 0 1,1 -8.4,0"/>
    <path android:strokeColor="#FFC93C" android:strokeWidth="2.6" android:strokeLineCap="round" android:pathData="M92.7,18.4v9.6M99.5,18.4v9.6"/>
    <path android:fillColor="#FFC93C" android:pathData="M99.5,14.8m-1.6,0a1.6,1.6 0 1,1 3.2,0a1.6,1.6 0 1,1 -3.2,0"/>
</vector>
"""

# 状态栏通知 / 快捷磁贴 / 悬浮球 图标
IC_STAT_DSH_XML = """<!-- 问问Ai status bar & floating ball icon -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="120"
    android:viewportHeight="120">
    <path android:fillColor="#FFC93C" android:pathData="M22,58h14L20,74z"/>
    <path android:fillColor="#FFC93C" android:pathData="M30,16h26a16,16 0 0,1 16,16v12a16,16 0 0,1 -16,16h-26a16,16 0 0,1 -16,-16v-12a16,16 0 0,1 16,-16z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M72,92h20l2,16z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M55,42h30a18,18 0 0,1 18,18v16a18,18 0 0,1 -18,18h-30a18,18 0 0,1 -18,-18v-16a18,18 0 0,1 18,-18z"/>
    <path android:strokeColor="#2F5BFF" android:strokeWidth="6" android:strokeLineCap="round" android:pathData="M61,60c0,-8 18,-8 18,1c0,7 -9,7 -9,14"/>
    <path android:fillColor="#2F5BFF" android:pathData="M70,84m-3.6,0a3.6,3.6 0 1,1 7.2,0a3.6,3.6 0 1,1 -7.2,0"/>
</vector>
"""


def replace_zh_brand_text(text: str, app_name: str, slogan: str, domain: str) -> str:
    """替换 XML / Python 字符串表中的中文品牌词，保留代码标识符与 URL 属性。"""
    # 1. 核心标语与名称精确替换
    text = re.sub(
        r'(<string name="app_name">)[^<]*(</string>)',
        rf'\g<1>{app_name}\g<2>',
        text,
    )
    text = re.sub(
        r'(<string name="tile_label">)[^<]*(</string>)',
        rf'\g<1>{app_name}\g<2>',
        text,
    )
    text = re.sub(
        r'(<string name="hero_title">)[^<]*(</string>)',
        rf'\g<1>{slogan}\g<2>',
        text,
    )
    text = re.sub(
        r'(<string name="about_disclaimer">)[^<]*(</string>)',
        rf'\g<1>{slogan}（官方网站 https://{domain}）· 基于 DeepSeek Harness 构建。\g<2>',
        text,
    )
    # 2. 将中文文案中的 DSH-Android 与 DSH 替换为 问问Ai（排除 dsh.bundle、dsh-android 等小写技术词）
    text = text.replace("DSH-Android", app_name)
    text = re.sub(r'(?<![A-Za-z0-9_/-])DSH(?![A-Za-z0-9_/-])', app_name, text)
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    p.add_argument("--assets-dir", type=Path, default=None)
    p.add_argument("--app-name", default="问问Ai")
    p.add_argument("--app-name-en", default="Wenwen.ai")
    p.add_argument("--slogan", default="遇事不决，问问Ai")
    p.add_argument("--slogan-en", default="Ask Wenwen.ai")
    p.add_argument("--domain", default="wenwenai.cn")
    p.add_argument("--github-repo", default="tongwei0715/DSH-Android")
    args = p.parse_args()

    root = args.repo_root.resolve()
    assets = (args.assets_dir or (root / "brand_assets")).resolve()
    res_dir = root / "app" / "src" / "main" / "res"

    # 1. 拷贝 mipmap-* 图标与自适应图标配置
    src_res = assets / "res"
    if src_res.is_dir():
        for folder in src_res.iterdir():
            if folder.is_dir() and folder.name.startswith("mipmap-"):
                dst = res_dir / folder.name
                dst.mkdir(parents=True, exist_ok=True)
                for f in folder.iterdir():
                    if f.is_file():
                        shutil.copy2(f, dst / f.name)
        print("[1/6] 已同步 mipmap-* 全套分辨率图标")

    # 写入矢量图标与背景色
    (res_dir / "values" / "colors.xml").write_text(
        '<resources>\n    <color name="launcher_bg">#FF2F5BFF</color>\n    <color name="ic_launcher_background">#FF2F5BFF</color>\n</resources>\n',
        encoding="utf-8",
    )
    (res_dir / "drawable" / "ic_launcher_fg.xml").write_text(IC_LAUNCHER_FG_XML, encoding="utf-8")
    (res_dir / "drawable" / "dsw_whale.xml").write_text(DSW_WHALE_XML, encoding="utf-8")
    (res_dir / "drawable" / "ic_stat_dsh.xml").write_text(IC_STAT_DSH_XML, encoding="utf-8")
    # 确保 mipmap-anydpi/ic_launcher.xml 使用矢量 ic_launcher_fg 且不加单色 monochrome 遮罩
    (res_dir / "mipmap-anydpi" / "ic_launcher.xml").write_text(
        '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
        '    <background android:drawable="@color/launcher_bg"/>\n'
        '    <foreground android:drawable="@drawable/ic_launcher_fg"/>\n'
        '</adaptive-icon>\n',
        encoding="utf-8",
    )
    anydpi_v26 = res_dir / "mipmap-anydpi-v26"
    if anydpi_v26.is_dir():
        shutil.rmtree(anydpi_v26)
    print("[2/6] 已更新 ic_launcher_fg.xml / dsw_whale.xml / ic_stat_dsh.xml 与主题背景色 #2F5BFF")

    # 2. 更新 Brand.kt 与 SettingsScreen.kt 中的硬编码品牌词与 Logo 比例
    brand_kt = root / "app/src/main/java/io/github/jackwener/dsh/core/designsystem/Brand.kt"
    if brand_kt.is_file():
        btxt = brand_kt.read_text(encoding="utf-8")
        btxt = re.sub(
            r'fun Whale\([^\n]+\n\s*Icon\([^\n]+',
            'fun Whale(modifier: Modifier = Modifier, width: Dp = 34.dp, tint: Color = Color.Unspecified) =\n'
            '    Icon(painterResource(R.drawable.dsw_whale), null, modifier.size(width), tint = Color.Unspecified)',
            btxt,
        )
        btxt = btxt.replace('Text("deepseek",', f'Text("{args.app_name}",')
        btxt = btxt.replace('Text("HARNESS",', f'Text("{args.domain.upper()}",')
        brand_kt.write_text(btxt, encoding="utf-8")
        print("[3/6] 已更新 Brand.kt 侧边栏 Wordmark 与全彩 Logo 渲染")

    settings_kt = root / "app/src/main/java/io/github/jackwener/dsh/feature/settings/SettingsScreen.kt"
    if settings_kt.is_file():
        stxt = settings_kt.read_text(encoding="utf-8")
        stxt = stxt.replace('SettingsRow("DSH",', f'SettingsRow("{args.app_name}",')
        settings_kt.write_text(stxt, encoding="utf-8")
        print("[4/6] 已更新 SettingsScreen.kt 关于页标题")

    # 3. 更新 strings*.xml 与 tools/ui/strings.py
    for xml_file in (res_dir / "values").glob("strings*.xml"):
        txt = xml_file.read_text(encoding="utf-8")
        xml_file.write_text(replace_zh_brand_text(txt, args.app_name, args.slogan, args.domain), encoding="utf-8")

    for lang_dir in ["values-en", "values-ru"]:
        sfile = res_dir / lang_dir / "strings.xml"
        if sfile.is_file():
            txt = sfile.read_text(encoding="utf-8")
            txt = re.sub(r'(<string name="app_name">)[^<]*(</string>)', rf'\g<1>{args.app_name_en}\g<2>', txt)
            txt = re.sub(r'(<string name="hero_title">)[^<]*(</string>)', rf'\g<1>{args.slogan_en}\g<2>', txt)
            sfile.write_text(txt, encoding="utf-8")
    print("[5/6] 已更新全套中英俄 strings*.xml 品牌名与口号「遇事不决，问问Ai」")

    # 4. 更新 UpdateManifest.kt 与 tools/make-update-manifest.py 指向 wenwenai.cn 与自有 GitHub 仓库
    um_kt = root / "app/src/main/java/io/github/jackwener/dsh/core/update/UpdateManifest.kt"
    if um_kt.is_file():
        utxt = um_kt.read_text(encoding="utf-8")
        utxt = re.sub(
            r'private const val REPO = "[^"]+"',
            f'private const val REPO = "{args.github_repo}"',
            utxt,
        )
        utxt = utxt.replace('"DSH-Android-$name.apk"', '"WenWen-$name-arm64.apk"')
        if f"https://{args.domain}/update/latest.json" not in utxt:
            utxt = utxt.replace(
                'val SOURCES = listOf(\n',
                f'val SOURCES = listOf(\n            "https://{args.domain}/update/latest.json",\n',
            )
        um_kt.write_text(utxt, encoding="utf-8")

    mk_py = root / "tools/make-update-manifest.py"
    if mk_py.is_file():
        mtxt = mk_py.read_text(encoding="utf-8")
        mtxt = re.sub(
            r'DEFAULT_REPO = "[^"]+"',
            f'DEFAULT_REPO = "{args.github_repo}"',
            mtxt,
        )
        mk_py.write_text(mtxt, encoding="utf-8")
    print(f"[6/6] 已将应用内更新源重定向至 https://{args.domain}/update/latest.json 与 {args.github_repo}")


if __name__ == "__main__":
    main()
