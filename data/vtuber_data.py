import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json


def create_sample_vtuber_data():
    """にじさんじJPライバーのサンプルデータを作成"""

    # 実際のにじさんじJPライバーの一部をサンプルデータとして作成
    vtubers = [
        {
            "name": "月ノ美兎",
            "debut_date": "2018-02-08",
            "gender": "女性",
            "voice_type": "高音",
            "personality_traits": ["しっかり者", "ツッコミ", "知的"],
            "streaming_genres": ["雑談", "ゲーム", "歌"],
            "game_genres": ["FPS", "RPG", "パズル"],
            "main_streaming_time": "夜",
            "subscriber_count": 850000,
            "average_viewers": 15000,
            "streaming_frequency": 5,  # 週あたりの配信回数
            "collab_frequency": 3,  # 月あたりのコラボ回数
            "singing_skill": 8,  # 1-10スケール
            "gaming_skill": 7,
            "talk_skill": 9,
            "avatar_color_theme": "白・青",
        },
        {
            "name": "樋口楓",
            "debut_date": "2018-05-07",
            "gender": "女性",
            "voice_type": "中音",
            "personality_traits": ["おっとり", "天然", "優しい"],
            "streaming_genres": ["雑談", "ゲーム", "お絵描き"],
            "game_genres": ["アクション", "シミュレーション", "RPG"],
            "main_streaming_time": "昼",
            "subscriber_count": 720000,
            "average_viewers": 12000,
            "streaming_frequency": 4,
            "collab_frequency": 5,
            "singing_skill": 6,
            "gaming_skill": 6,
            "talk_skill": 8,
            "avatar_color_theme": "緑・茶",
        },
        {
            "name": "叶",
            "debut_date": "2018-05-07",
            "gender": "男性",
            "voice_type": "低音",
            "personality_traits": ["冷静", "分析的", "紳士"],
            "streaming_genres": ["ゲーム", "雑談", "歌"],
            "game_genres": ["FPS", "格闘", "ホラー"],
            "main_streaming_time": "夜",
            "subscriber_count": 950000,
            "average_viewers": 18000,
            "streaming_frequency": 6,
            "collab_frequency": 4,
            "singing_skill": 9,
            "gaming_skill": 9,
            "talk_skill": 8,
            "avatar_color_theme": "黒・青",
        },
        {
            "name": "リゼ・ヘルエスタ",
            "debut_date": "2019-01-30",
            "gender": "女性",
            "voice_type": "中音",
            "personality_traits": ["お姉さん", "落ち着いている", "知的"],
            "streaming_genres": ["雑談", "ゲーム", "ASMR"],
            "game_genres": ["RPG", "シミュレーション", "パズル"],
            "main_streaming_time": "夜",
            "subscriber_count": 680000,
            "average_viewers": 11000,
            "streaming_frequency": 4,
            "collab_frequency": 2,
            "singing_skill": 7,
            "gaming_skill": 6,
            "talk_skill": 9,
            "avatar_color_theme": "紫・白",
        },
        {
            "name": "椎名唯華",
            "debut_date": "2018-07-06",
            "gender": "女性",
            "voice_type": "高音",
            "personality_traits": ["元気", "明るい", "ギャル"],
            "streaming_genres": ["雑談", "ゲーム", "歌"],
            "game_genres": ["カジュアル", "音ゲー", "パーティ"],
            "main_streaming_time": "夕方",
            "subscriber_count": 590000,
            "average_viewers": 9000,
            "streaming_frequency": 5,
            "collab_frequency": 6,
            "singing_skill": 8,
            "gaming_skill": 5,
            "talk_skill": 9,
            "avatar_color_theme": "ピンク・白",
        },
        {
            "name": "剣持刀也",
            "debut_date": "2018-05-17",
            "gender": "男性",
            "voice_type": "中音",
            "personality_traits": ["面白い", "ボケ", "親しみやすい"],
            "streaming_genres": ["雑談", "ゲーム", "企画"],
            "game_genres": ["バラエティ", "パーティ", "レトロ"],
            "main_streaming_time": "夜",
            "subscriber_count": 780000,
            "average_viewers": 13000,
            "streaming_frequency": 5,
            "collab_frequency": 7,
            "singing_skill": 6,
            "gaming_skill": 7,
            "talk_skill": 10,
            "avatar_color_theme": "青・白",
        },
        {
            "name": "白雪巴",
            "debut_date": "2019-02-16",
            "gender": "女性",
            "voice_type": "中音",
            "personality_traits": ["癒し系", "おっとり", "優しい"],
            "streaming_genres": ["雑談", "ゲーム", "歌"],
            "game_genres": ["RPG", "シミュレーション", "アドベンチャー"],
            "main_streaming_time": "夕方",
            "subscriber_count": 520000,
            "average_viewers": 8000,
            "streaming_frequency": 3,
            "collab_frequency": 3,
            "singing_skill": 9,
            "gaming_skill": 5,
            "talk_skill": 7,
            "avatar_color_theme": "白・水色",
        },
        {
            "name": "文野環",
            "debut_date": "2018-07-06",
            "gender": "女性",
            "voice_type": "高音",
            "personality_traits": ["元気", "活発", "ポジティブ"],
            "streaming_genres": ["雑談", "ゲーム", "歌"],
            "game_genres": ["アクション", "スポーツ", "音ゲー"],
            "main_streaming_time": "昼",
            "subscriber_count": 480000,
            "average_viewers": 7500,
            "streaming_frequency": 4,
            "collab_frequency": 5,
            "singing_skill": 7,
            "gaming_skill": 8,
            "talk_skill": 8,
            "avatar_color_theme": "オレンジ・白",
        },
        {
            "name": "でびでび・でびる",
            "debut_date": "2018-11-30",
            "gender": "男性",
            "voice_type": "特殊",
            "personality_traits": ["個性的", "ユニーク", "愛らしい"],
            "streaming_genres": ["雑談", "ゲーム", "企画"],
            "game_genres": ["バラエティ", "カジュアル", "パズル"],
            "main_streaming_time": "夜",
            "subscriber_count": 620000,
            "average_viewers": 10000,
            "streaming_frequency": 4,
            "collab_frequency": 4,
            "singing_skill": 5,
            "gaming_skill": 6,
            "talk_skill": 8,
            "avatar_color_theme": "赤・黒",
        },
        {
            "name": "社築",
            "debut_date": "2018-05-17",
            "gender": "男性",
            "voice_type": "低音",
            "personality_traits": ["クール", "落ち着いている", "大人"],
            "streaming_genres": ["ゲーム", "雑談", "歌"],
            "game_genres": ["FPS", "戦略", "シミュレーション"],
            "main_streaming_time": "夜",
            "subscriber_count": 710000,
            "average_viewers": 12500,
            "streaming_frequency": 5,
            "collab_frequency": 3,
            "singing_skill": 8,
            "gaming_skill": 9,
            "talk_skill": 7,
            "avatar_color_theme": "灰・黒",
        },
    ]

    return pd.DataFrame(vtubers)


def encode_categorical_features(df):
    """カテゴリカル特徴量を数値化"""

    # 性別をエンコード
    df["gender_encoded"] = df["gender"].map({"女性": 0, "男性": 1})

    # 声質をエンコード
    voice_type_mapping = {"高音": 0, "中音": 1, "低音": 2, "特殊": 3}
    df["voice_type_encoded"] = df["voice_type"].map(voice_type_mapping)

    # 配信時間をエンコード
    time_mapping = {"昼": 0, "夕方": 1, "夜": 2}
    df["main_streaming_time_encoded"] = df["main_streaming_time"].map(time_mapping)

    # 配信ジャンルの数値化（ワンホットエンコーディング）
    all_streaming_genres = set()
    for genres in df["streaming_genres"]:
        all_streaming_genres.update(genres)

    for genre in all_streaming_genres:
        df[f"streaming_{genre}"] = df["streaming_genres"].apply(
            lambda x: 1 if genre in x else 0
        )

    # ゲームジャンルの数値化
    all_game_genres = set()
    for genres in df["game_genres"]:
        all_game_genres.update(genres)

    for genre in all_game_genres:
        df[f"game_{genre}"] = df["game_genres"].apply(lambda x: 1 if genre in x else 0)

    # 性格特性の数値化
    all_personality_traits = set()
    for traits in df["personality_traits"]:
        all_personality_traits.update(traits)

    for trait in all_personality_traits:
        df[f"personality_{trait}"] = df["personality_traits"].apply(
            lambda x: 1 if trait in x else 0
        )

    return df


def perform_clustering(df, n_clusters=4):
    """クラスタリングを実行"""

    # 数値特徴量を選択
    numerical_features = [
        "subscriber_count",
        "average_viewers",
        "streaming_frequency",
        "collab_frequency",
        "singing_skill",
        "gaming_skill",
        "talk_skill",
        "gender_encoded",
        "voice_type_encoded",
        "main_streaming_time_encoded",
    ]

    # ワンホットエンコードされた特徴量を追加
    encoded_features = [
        col
        for col in df.columns
        if col.startswith(("streaming_", "game_", "personality_"))
    ]
    all_features = numerical_features + encoded_features

    # 特徴量が存在するかチェック
    available_features = [f for f in all_features if f in df.columns]

    # データフレームをコピーして作業用に使用
    df_work = df.copy()
    X = df_work[available_features].fillna(0)

    # すべて数値型であることを確認
    X = X.select_dtypes(include=[np.number])

    print(f"Using {len(X.columns)} features for clustering: {list(X.columns)}")

    # 標準化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # クラスタリング
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    df["cluster"] = clusters

    return df, clusters, scaler, kmeans


def load_vtuber_data():
    """Vtuberデータをロードしてクラスタリングを実行"""

    # データ作成
    df = create_sample_vtuber_data()

    # カテゴリカル特徴量のエンコード
    df = encode_categorical_features(df)

    # クラスタリング実行
    df, clusters, scaler, kmeans = perform_clustering(df)

    return df, clusters, scaler


def get_cluster_characteristics(df):
    """各クラスタの特徴を分析"""

    cluster_chars = {}

    for cluster_id in df["cluster"].unique():
        cluster_data = df[df["cluster"] == cluster_id]

        # 各クラスタの代表的な特徴を計算
        chars = {
            "size": len(cluster_data),
            "avg_subscribers": cluster_data["subscriber_count"].mean(),
            "avg_viewers": cluster_data["average_viewers"].mean(),
            "common_genres": [],
            "common_personality": [],
            "main_gender": cluster_data["gender"].mode().iloc[0]
            if len(cluster_data["gender"].mode()) > 0
            else "mixed",
            "main_voice_type": cluster_data["voice_type"].mode().iloc[0]
            if len(cluster_data["voice_type"].mode()) > 0
            else "mixed",
            "main_streaming_time": cluster_data["main_streaming_time"].mode().iloc[0]
            if len(cluster_data["main_streaming_time"].mode()) > 0
            else "mixed",
        }

        # よく見られる配信ジャンル
        genre_counts = {}
        for genres in cluster_data["streaming_genres"]:
            for genre in genres:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        chars["common_genres"] = sorted(
            genre_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]

        # よく見られる性格特性
        trait_counts = {}
        for traits in cluster_data["personality_traits"]:
            for trait in traits:
                trait_counts[trait] = trait_counts.get(trait, 0) + 1
        chars["common_personality"] = sorted(
            trait_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]

        cluster_chars[cluster_id] = chars

    return cluster_chars


if __name__ == "__main__":
    # テスト実行
    df, clusters, scaler = load_vtuber_data()
    print("データロード完了")
    print(f"ライバー数: {len(df)}")
    print(f"クラスタ数: {len(set(clusters))}")

    cluster_chars = get_cluster_characteristics(df)
    for cluster_id, chars in cluster_chars.items():
        print(f"\nクラスタ {cluster_id}:")
        print(f"  サイズ: {chars['size']}")
        print(f"  平均登録者数: {chars['avg_subscribers']:,.0f}")
        print(f"  主な性別: {chars['main_gender']}")
        print(f"  主な配信ジャンル: {[g[0] for g in chars['common_genres']]}")
