"""下载 unstructured 解析文档时要用的 NLTK 数据。

`unstructured` 在切分文档时会用 NLTK 的分句器和词性标注器。课程原始资料
把这批数据（约 58MB、39 个 pickle 文件、18 种语言）直接打包进了仓库，
这里改成按需下载，原因有两个：

  1. 它是第三方模型数据，不是项目代码，没必要进 git 历史；
  2. pickle 加载等于执行代码，仓库里躺着一堆来历不明的 pickle 不是好事 ——
     由 NLTK 官方渠道下载，至少来源是清楚的。

用法（在 llmops-api 目录下，激活虚拟环境后）：

    python scripts/download_nltk_data.py

Docker 构建时会自动执行这一步，见 Dockerfile。
"""
import os
import sys

# 和 Dockerfile 里的 ENV NLTK_DATA 保持一致
TARGET = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "internal", "core", "unstructured", "nltk_data",
)

# unstructured 实际会用到的几个包。不下全量语言模型 —— 本项目只处理中英文，
# 波兰语、希腊语那些分句器加起来几十 MB，用不上。
PACKAGES = [
    "punkt_tab",                        # 分句（新版，unstructured >= 0.16 用这个）
    "averaged_perceptron_tagger_eng",   # 英文词性标注
]


def main() -> int:
    try:
        import nltk
    except ImportError:
        print("错误：没装 nltk。先跑 pip install -r requirements.txt")
        return 1

    os.makedirs(TARGET, exist_ok=True)
    print(f"下载目标：{TARGET}")

    failed = []
    for pkg in PACKAGES:
        print(f"  正在下载 {pkg} …")
        if not nltk.download(pkg, download_dir=TARGET, quiet=True):
            failed.append(pkg)

    if failed:
        print(f"\n以下包下载失败：{failed}")
        print("可能是网络问题，重试一次通常就好。")
        return 1

    total = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, fs in os.walk(TARGET) for f in fs
    )
    print(f"\n完成，共 {total / 1048576:.1f} MB")
    print("提示：运行时需要设置环境变量 NLTK_DATA 指向上面这个目录，")
    print("      Dockerfile 里已经设好了。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
