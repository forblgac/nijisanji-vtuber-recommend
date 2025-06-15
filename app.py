from flask import Flask, render_template, request, jsonify
import json
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.express as px
from datetime import datetime

app = Flask(__name__)

# グローバル変数でデータを保持
vtuber_data = None
clusters = None
scaler = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/vtubers")
def get_vtubers():
    global vtuber_data
    if vtuber_data is not None:
        return jsonify(vtuber_data.to_dict("records"))
    return jsonify([])


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json

    # ユーザーの選択に基づいて推薦を実行
    preferences = {
        "streaming_genre": data.get("streaming_genre", []),
        "game_genre": data.get("game_genre", []),
        "streaming_time": data.get("streaming_time", ""),
        "gender": data.get("gender", ""),
        "voice_type": data.get("voice_type", ""),
        "personality": data.get("personality", []),
    }

    recommended_vtubers = calculate_recommendations(preferences)
    return jsonify(recommended_vtubers)


def calculate_recommendations(preferences):
    global vtuber_data, clusters

    if vtuber_data is None:
        return []

    # 推薦スコアを計算
    scores = []
    for idx, vtuber in vtuber_data.iterrows():
        score = 0

        # 配信ジャンルのマッチング
        if preferences["streaming_genre"]:
            genre_matches = sum(
                1
                for genre in preferences["streaming_genre"]
                if genre in vtuber.get("streaming_genres", [])
            )
            score += genre_matches * 3

        # ゲームジャンルのマッチング
        if preferences["game_genre"]:
            game_matches = sum(
                1
                for game in preferences["game_genre"]
                if game in vtuber.get("game_genres", [])
            )
            score += game_matches * 2

        # 配信時間のマッチング
        if preferences["streaming_time"] and preferences[
            "streaming_time"
        ] == vtuber.get("main_streaming_time"):
            score += 5

        # 性別のマッチング
        if preferences["gender"] and preferences["gender"] == vtuber.get("gender"):
            score += 2

        # 声質のマッチング
        if preferences["voice_type"] and preferences["voice_type"] == vtuber.get(
            "voice_type"
        ):
            score += 3

        # 性格のマッチング
        if preferences["personality"]:
            personality_matches = sum(
                1
                for trait in preferences["personality"]
                if trait in vtuber.get("personality_traits", [])
            )
            score += personality_matches * 2

        scores.append((score, vtuber.to_dict()))

    # スコア順でソート
    scores.sort(key=lambda x: x[0], reverse=True)
    return [vtuber for score, vtuber in scores[:10]]


@app.route("/api/load_mcp_data", methods=["POST"])
def load_mcp_data():
    """MCPサーバーから最新のライバーデータを取得"""
    global vtuber_data, clusters, scaler

    try:
        # MCPデータローダーを試行
        from data.mcp_data_loader import load_mcp_vtuber_data

        mcp_vtubers = load_mcp_vtuber_data()

        if mcp_vtubers:
            # MCPデータをDataFrameに変換
            import pandas as pd
            from data.vtuber_data import encode_categorical_features, perform_clustering

            df = pd.DataFrame(mcp_vtubers)
            df = encode_categorical_features(df)
            df, new_clusters, new_scaler, kmeans = perform_clustering(df)

            # グローバル変数を更新
            vtuber_data = df
            clusters = new_clusters
            scaler = new_scaler

            return jsonify(
                {
                    "success": True,
                    "message": f"MCPサーバーから{len(mcp_vtubers)}名のライバーデータを取得しました",
                    "vtuber_count": len(mcp_vtubers),
                }
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "message": "MCPサーバーからデータを取得できませんでした",
                }
            ), 400

    except Exception as e:
        return jsonify(
            {"success": False, "message": f"エラーが発生しました: {str(e)}"}
        ), 500


if __name__ == "__main__":
    # データを初期化
    from data.vtuber_data import load_vtuber_data, perform_clustering

    vtuber_data, clusters, scaler = load_vtuber_data()
    app.run(debug=True, host="0.0.0.0", port=8080)
