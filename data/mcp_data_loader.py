import json
import re
import subprocess
import sys
import time
from typing import List, Dict, Any, Optional


class MCPDataLoader:
    """MCPサーバーからにじさんじライバーデータを取得するクラス"""

    def __init__(self):
        import os

        # プロジェクトのルートディレクトリを取得
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.mcp_server_path = os.path.join(
            project_root, "mcp-server", "build", "index.js"
        )

    def call_mcp_tool(
        self, tool_name: str, arguments: Dict[str, Any] = None
    ) -> Optional[Dict]:
        """MCPツールを呼び出す"""
        if arguments is None:
            arguments = {}

        try:
            # MCPサーバーを起動してツールを呼び出す
            cmd = ["node", self.mcp_server_path]
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # MCP初期化メッセージ
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "recommend-vtuber", "version": "1.0.0"},
                },
            }

            # ツール呼び出しメッセージ
            tool_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            }

            # メッセージを送信
            input_data = (
                json.dumps(init_message) + "\n" + json.dumps(tool_message) + "\n"
            )
            stdout, stderr = process.communicate(input=input_data, timeout=30)

            if process.returncode != 0:
                print(f"MCP error: {stderr}")
                return None

            # レスポンスを解析
            lines = stdout.strip().split("\n")
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("id") == 2 and "result" in response:
                            content = response["result"].get("content", [])
                            if content and len(content) > 0:
                                return json.loads(content[0]["text"])
                    except json.JSONDecodeError:
                        continue

            return None

        except subprocess.TimeoutExpired:
            process.kill()
            print("MCP call timed out")
            return None
        except Exception as e:
            print(f"Error calling MCP tool: {e}")
            return None

    def get_vtuber_list(self) -> List[str]:
        """ライバー一覧を取得"""
        try:
            result = self.call_mcp_tool("get_vtuber_list")
            if result and "vtubers" in result:
                # 日本語名のライバーのみフィルタリング
                japanese_vtubers = []
                for name in result["vtubers"]:
                    # 日本語文字が含まれているかチェック
                    if re.search(r"[ひ-ろ・ヽヾ゠-ー一-龯]", name):
                        # グループ名やイベント名を除外
                        exclude_terms = [
                            "NIJISANJI",
                            "NIJI",
                            "KZHCUP",
                            "MARIO KART",
                            "TEKKEN",
                            "SitR",
                            "HEROES",
                            "COLORS",
                            "VOLTACTION",
                        ]
                        if not any(term in name for term in exclude_terms):
                            japanese_vtubers.append(name)

                return japanese_vtubers[:50]  # 最大50名に制限
            return []
        except Exception as e:
            print(f"Error getting vtuber list: {e}")
            return []

    def get_vtuber_details_batch(
        self, names: List[str], batch_size: int = 10
    ) -> List[Dict]:
        """複数のライバーの詳細情報を取得"""
        all_vtubers = []

        # バッチ処理で取得
        for i in range(0, len(names), batch_size):
            batch_names = names[i : i + batch_size]
            print(f"Fetching batch {i // batch_size + 1}: {len(batch_names)} vtubers")

            try:
                result = self.call_mcp_tool(
                    "get_multiple_vtuber_details",
                    {"names": batch_names, "limit": batch_size},
                )

                if result and "vtubers" in result:
                    all_vtubers.extend(result["vtubers"])

                # レート制限を避けるため少し待機
                time.sleep(2)

            except Exception as e:
                print(f"Error fetching batch {i // batch_size + 1}: {e}")
                continue

        return all_vtubers

    def enhance_vtuber_data(self, vtuber_data: Dict) -> Dict:
        """ライバーデータを推薦システム用に補完"""
        enhanced = vtuber_data.copy()

        # 欠損データの補完
        if "gender" not in enhanced or not enhanced["gender"]:
            # 名前から性別を推定（簡易版）
            name = enhanced.get("name", "")
            if any(
                char in name
                for char in ["美", "華", "花", "姫", "音", "愛", "香", "桜", "月", "星"]
            ):
                enhanced["gender"] = "女性"
            else:
                enhanced["gender"] = "男性"  # デフォルト

        # 声質の推定
        if "voice_type" not in enhanced or not enhanced["voice_type"]:
            if enhanced["gender"] == "女性":
                enhanced["voice_type"] = "高音"
            else:
                enhanced["voice_type"] = "低音"

        # 配信時間の推定
        if "main_streaming_time" not in enhanced or not enhanced["main_streaming_time"]:
            enhanced["main_streaming_time"] = "夜"  # デフォルト

        # 数値データの補完
        if "subscriber_count" not in enhanced or not enhanced["subscriber_count"]:
            enhanced["subscriber_count"] = 500000  # デフォルト値

        if "average_viewers" not in enhanced or not enhanced["average_viewers"]:
            # 登録者数の5-10%を視聴者数とする
            enhanced["average_viewers"] = int(enhanced["subscriber_count"] * 0.07)

        # スキル値の推定
        enhanced["streaming_frequency"] = 4  # 週4回
        enhanced["collab_frequency"] = 3  # 月3回

        # 配信ジャンルに基づいてスキルを推定
        streaming_genres = enhanced.get("streaming_genres", [])
        enhanced["singing_skill"] = 8 if "歌" in streaming_genres else 5
        enhanced["gaming_skill"] = 8 if "ゲーム" in streaming_genres else 5
        enhanced["talk_skill"] = 9 if "雑談" in streaming_genres else 6

        # アバターカラーテーマの推定
        if "avatar_color_theme" not in enhanced or not enhanced["avatar_color_theme"]:
            color_themes = [
                "白・青",
                "緑・茶",
                "黒・青",
                "紫・白",
                "ピンク・白",
                "青・白",
                "白・水色",
                "オレンジ・白",
                "赤・黒",
                "灰・黒",
            ]
            enhanced["avatar_color_theme"] = color_themes[
                hash(enhanced["name"]) % len(color_themes)
            ]

        # デビュー日の補完
        if "debut_date" not in enhanced or not enhanced["debut_date"]:
            enhanced["debut_date"] = "2018-01-01"  # デフォルト

        return enhanced


def load_mcp_vtuber_data():
    """MCPサーバーからライバーデータを取得して推薦システム用に変換"""
    loader = MCPDataLoader()

    print("ライバー一覧を取得中...")
    vtuber_names = loader.get_vtuber_list()
    print(f"取得したライバー数: {len(vtuber_names)}")

    if not vtuber_names:
        print("ライバー一覧の取得に失敗しました")
        return []

    print("ライバー詳細情報を取得中...")
    vtuber_details = loader.get_vtuber_details_batch(vtuber_names, batch_size=5)
    print(f"詳細情報を取得したライバー数: {len(vtuber_details)}")

    # データを推薦システム用に変換・補完
    enhanced_vtubers = []
    for vtuber in vtuber_details:
        if vtuber:  # Noneでない場合のみ処理
            enhanced = loader.enhance_vtuber_data(vtuber)
            enhanced_vtubers.append(enhanced)

    print(f"最終的なライバー数: {len(enhanced_vtubers)}")
    return enhanced_vtubers


if __name__ == "__main__":
    # テスト実行
    vtubers = load_mcp_vtuber_data()
    print(f"\n取得完了: {len(vtubers)}名のライバー")

    if vtubers:
        print("\n最初の3名のサンプル:")
        for i, vtuber in enumerate(vtubers[:3]):
            print(f"{i + 1}. {vtuber['name']}")
            print(f"   性別: {vtuber.get('gender', '不明')}")
            print(f"   配信ジャンル: {vtuber.get('streaming_genres', [])}")
            print(f"   性格: {vtuber.get('personality_traits', [])}")
            print()
