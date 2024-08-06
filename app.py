import json
import time
from typing import Optional
from urllib.parse import urlparse

import requests
import streamlit as st

PROMPTS = """\
================================================================
WebpagePack Output File
================================================================

Purpose:
--------
This file contains a packed content of the multiple web pages' contents about a specific topic.
It is designed to be easily consumable by AI systems for analysis, summarize, or other automated processes.

File Format:
------------
The content is organized as follows:
1. This header section
2. Multiple web page entries, each consisting of:
  a. A separator line (================)
  b. The title of web page (Title: )
  c. The URL of web page (URL: )
  d. Another separator line
  e. The full text contents of the web page formatted with Markdown
  f. A blank line

Usage Guidelines:
-----------------
1. This file should be treated as read-only.
2. When processing this file, use the separators and "Title:" and "URL:" markers to distinguish contexts between different web pages in this analysis.

Notes:
------
- Some pages may have useless information such as page header, page footer, website menus and links to other pages. You should ignore these as needed.
- Binary data are not included in this packed representation.

================================================================
Web Pages Contents
================================================================
"""

SEP = "================"
OUTPUT_FILE_NAME = "webpagepack-output.txt"
SLEEP = 1
FIRECRAWL_CLOUD_API_URL = "https://api.firecrawl.dev/v0/scrape"


def is_valid_url(url: str) -> bool:
    """URLが有効かどうかをチェックする"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_json(json_text: str) -> dict:
    """FireCrawlのJSONレスポンスからタイトル、URL、コンテンツを抽出する."""
    page_obj = json.loads(json_text)
    return {
        "Title": page_obj["data"]["metadata"]["title"],
        "URL Source": page_obj["data"]["metadata"]["sourceURL"],
        "Markdown Content": page_obj["data"]["markdown"],
    }


def pack_output(urls_content: list[dict]) -> str:
    """複数のWebページの内容を1つのテキストにパックする"""
    output_text_all = PROMPTS
    for u in urls_content:
        output_text_each = f"""
{SEP}
Title: {u['Title']}
URL: {u['URL Source']}
{SEP}

{u['Markdown Content']}

"""
        output_text_all += output_text_each

    return output_text_all


def read_url(url: str, host: str, api_key: str) -> Optional[str]:
    """FireCrawlでURLのコンテンツを取得する"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": url,
        "pageOptions": {
            "onlyMainContent": True,
        },
    }
    response = requests.request(
        "POST",
        host,
        json=payload,
        headers=headers,
    )
    response.raise_for_status()
    return response.text


def main():
    st.title("WebpagePack-FireCrawl")
    st.write(
        "複数のWebページの内容をFireCrawlで1つのファイルにパックしてAI処理用にします。"
    )

    # セッション状態の初期化
    if "packed_output" not in st.session_state:
        st.session_state.packed_output = None

    firecrawl_host_type = st.selectbox(
        label="FireCrawlのホスティングを選択:",
        options=["クラウド", "セルフホスト"],
        index=None,
        placeholder="リストから選択",
    )

    if firecrawl_host_type == "クラウド":
        firecrawl_host = st.text_input(
            label="FireCrawlのAPIエンドポイントURL:",
            value=FIRECRAWL_CLOUD_API_URL,
            type="default",
            disabled=True,
        )
        firecrawl_api_key = st.text_input(
            label="FireCrawlのAPIキーを入力:",
            type="password",
        )
    elif firecrawl_host_type == "セルフホスト":
        firecrawl_host = st.text_input(
            label="FireCrawlのAPIエンドポイントURLを入力(例: `http://localhost:3002/v0/scrape`):",
            type="default",
            disabled=False,
        )
        firecrawl_api_key = st.text_input(
            label="FireCrawlのAPIキーを入力(注: セルフホストでは認証不要と思われるためダミー値をデフォルトでは設定):",
            value="dummy",
            type="password",
        )
    else:
        st.session_state.firecrawl_host_visiblity = "invisible"
        st.session_state.firecrawl_host_disabled = True

    urls = st.text_area("URLを入力してください（1行に1つ）:", height=100)

    if st.button("URLを処理"):
        # 出力を初期化
        st.session_state.packed_output = None

        if not firecrawl_host_type:
            st.error("FireCrawlのホスティングタイプを選択してください。")
            return

        if not firecrawl_host:
            st.error("FireCrawlのエンドポイントURLを入力してください。")
            return

        if not is_valid_url(firecrawl_host):
            st.error(
                "FireCrawlのエンドポイントURLが正しくありません。修正してください。"
            )
            return

        if not firecrawl_api_key:
            st.error("FireCrawlのAPIキーを入力してください。")
            return

        # 入力URLチェック
        url_list = urls.strip().split("\n")
        invalid_urls = [url for url in url_list if not is_valid_url(url.strip())]

        if invalid_urls:
            st.error("無効なURLが含まれています:  \n" + "  \n".join(invalid_urls))
            return

        # スクレイピング
        urls_content = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_count = 0
        success_count = 0

        for i, url in enumerate(url_list, 1):
            status_text.text(f"処理中 {i}/{len(url_list)}: {url}")
            try:
                content = read_url(url.strip(), firecrawl_host, firecrawl_api_key)
                extracted_content = extract_json(content)
                urls_content.append(extracted_content)
                success_count += 1
            except requests.RequestException as e:
                st.warning(f"URL '{url}' の読み込み中にエラーが発生しました: {e}")
                error_count += 1
            except json.JSONDecodeError:
                st.warning(f"URL '{url}' のJSONデコードに失敗しました。")
                error_count += 1
            except KeyError as e:
                st.warning(f"URL '{url}' のデータにキーが含まれていません: {e}")
                error_count += 1
            except Exception as e:
                st.warning(f"URL '{url}' の処理中に予期せぬエラーが発生しました: {e}")
                error_count += 1
            finally:
                progress_bar.progress(i / len(url_list))
                time.sleep(SLEEP)

        if urls_content:
            st.session_state.packed_output = pack_output(urls_content)
            st.success(
                f"処理が完了しました。(成功: {success_count} | エラー: {error_count})  \n"
                f"結果を以下に表示します。"
            )
        else:
            st.error(
                "コンテンツを取得できませんでした。URLとAPIキーを再度確認してください。"
            )

    # 処理結果の表示とダウンロードボタン
    if st.session_state.packed_output:
        st.text_area(
            "パックされたコンテンツ", st.session_state.packed_output, height=300
        )

        st.markdown(f"合計文字数: {len(st.session_state.packed_output)}")

        st.download_button(
            label="ダウンロード",
            data=st.session_state.packed_output,
            file_name=OUTPUT_FILE_NAME,
            mime="text/plain",
        )


if __name__ == "__main__":
    main()
