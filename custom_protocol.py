import json

"""
カスタムプロトコル：Multiple Media Protocol（MMP）
ヘッダー（64 ビット）: JSONサイズ（2バイト）、メディアタイプサイズ（1バイト）、ペイロードサイズ（5 バイト）を含みます。
ボディ：最初の JSON サイズバイトは、すべての引数を含む JSON ファイルで、最大で 216バイト（64 KB）です。
    次のメディアタイプサイズバイトは、メディアタイプ（mp4、mp3、json、avi など）です。
    メディアタイプは UTF-8 でエンコードされ、1~4 バイトの幅を持つことができます。
    その後にペイロードが続き、そのサイズはペイロードサイズバイトで、最大 240 バイト(1TB)です。
    ペイロードは常にファイルとして格納され、メディアタイプに基づいたファイルタイプを持ち、メディアタイプに従って読み込まれることに注意しましょう。
"""


def pack_mmp_message(json_data: dict, media_type: str, payload: bytes):
    """
    MMPメッセージをパックする関数
    ヘッダーとボディを含む完全なMMPメッセージをバイト列として生成します

    Args:
        json_data: dict: すべての引数を含むjsonデータ。例: {"action": "convert", "quality": "high"}
        media_type: str: メディアタイプ。例: "mp4"。UTF-8でエンコードされる
        payload: bytes: 実際のファイルデータ

    Returns:
        bytes: パックされたMMPメッセージ

    Raises:
        ValueError: データサイズがプロトコルで定義された最大値を超過した場合
    """
    # MNPプロトコル定数
    # ヘッダー各部のバイトサイズ
    JSON_SIZE_BYTES = 2
    MEDIA_TYPE_SIZE_BYTES = 1
    PAYLOAD_SIZE_BYTES = 5
    # ヘッダー全体のバイトサイズ 8バイト
    # MMP_HEADER_SIZE = JSON_SIZE_BYTES + MEDIA_TYPE_SIZE_BYTES + PAYLOAD_SIZE_BYTES

    # 各要素の最大サイズ
    # JSONサイズ(約64KB)
    MAX_JSON_SIZE = (1 << (JSON_SIZE_BYTES * 8)) - 1
    # メディアタイプサイズ（255バイト）
    MAX_MEDIA_TYPE_SIZE = (1 << (MEDIA_TYPE_SIZE_BYTES * 8)) - 1
    # ペイロードサイズ(約1TB)
    MAX_PAYLOAD_SIZE = (1 << (PAYLOAD_SIZE_BYTES * 8)) - 1

    # jsonデータをバイト列にエンコードしてサイズを取得
    json_bytes = json.dumps(json_data).encode("utf-8")
    json_size = len(json_bytes)
    # メディアタイプをバイト列にエンコードしてサイズを取得
    media_type_bytes = media_type.encode("utf-8")
    media_type_size = len(media_type_bytes)
    # ペイロードデータのサイズを取得
    payload_size = len(payload)
    # デバッグ
    print(f"payload_size: {payload_size}")

    # サイズ制限のチェック
    if json_size > MAX_JSON_SIZE:
        raise ValueError(
            f"JSONサイズが最大値を超過しました: {json_size} > {MAX_JSON_SIZE}"
        )
    if media_type_size > MAX_MEDIA_TYPE_SIZE:
        raise ValueError(
            f"メディアタイプサイズが最大値を超過しました: {media_type_size} > {MAX_MEDIA_TYPE_SIZE}"
        )
    if payload_size > MAX_PAYLOAD_SIZE:
        raise ValueError(
            f"ペイロードサイズが最大値を超過しました: {payload_size} > {MAX_PAYLOAD_SIZE}"
        )

    # ヘッダーの構築
    # 各サイズをビッグエンディアン形式のバイト列に変換して連結
    header = bytearray()
    header += json_size.to_bytes(JSON_SIZE_BYTES, byteorder="big")
    header += media_type_size.to_bytes(MEDIA_TYPE_SIZE_BYTES, byteorder="big")
    header += payload_size.to_bytes(PAYLOAD_SIZE_BYTES, byteorder="big")

    # ボディの構築
    body = json_bytes + media_type_bytes + payload

    # ヘッダーとボディを連結して返す
    return header + body


def unpack_mmp_message(
    body_data: bytes,
    json_size: int,
    media_type_size: int,
    payload_size: int,
):
    # JSONデータの抽出
    json_data_bytes = body_data[0:json_size]

    # メディアタイプの抽出
    media_type_bytes = body_data[json_size : json_size + media_type_size]

    # ペイロードの抽出
    payload_data = body_data[
        json_size + media_type_size : json_size + media_type_size + payload_size
    ]
    # デバッグ
    print(f"payload_data: {len(payload_data)}")

    # バイト列を元の形式にデコード
    try:
        json_data = json.loads(json_data_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"unpack_mmp_message関数でJSONデータのデコードに失敗しました: {e}",
            e.doc,
            e.pos,
        )
    media_type = media_type_bytes.decode("utf-8")

    return json_data, media_type, payload_data
