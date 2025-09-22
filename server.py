import os
import socket

from dotenv import load_dotenv

from custom_protocol import pack_mmp_message, unpack_mmp_message
from ffmpeg_function import (
    change_video_aspect_ratio,
    compress_video_file,
    convert_to_mp3file,
    decode_and_save_video,
    resize_video_resolution,
    trim_video_to_gif_webm,
)

# 環境変数を読み込む
load_dotenv()


class Server:
    def __init__(self):
        self.server_running = True
        # バッファサイズ
        self.header_bytes: int = int(os.getenv("header_bytes", 8))
        self.body_bytes: int = int(os.getenv("body_bytes", 1400))
        # TCP設定
        self.tcp_port: int = int(os.getenv("port", 8888))
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 再利用許可
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(("0.0.0.0", self.tcp_port))
        # 接続を待機状態
        self.tcp_socket.listen()

    def server_start(self):
        """サーバーを起動する"""
        try:
            print(f"サーバー起動中....: {self.tcp_port}")
            while self.server_running:
                client_socket, client_address = self.tcp_socket.accept()
                print(f"クライアント:{client_address}とのソケットを受け付けました")

                # ヘッダーを取得
                header_data_bytes = client_socket.recv(self.header_bytes)
                # ヘッダーから各サイズを取得
                json_size = int.from_bytes(header_data_bytes[0:2], byteorder="big")
                media_type_size = int.from_bytes(header_data_bytes[2:3], byteorder="big")
                payload_size = int.from_bytes(header_data_bytes[3:9], byteorder="big")
                body_data_size = json_size + media_type_size + payload_size

                # 動画データ受信
                # 設計として基本的に1400バイトずつ受信する
                body_data = b""
                remaining = body_data_size
                while remaining > 0:
                    # 効率よく受信するため受信データの残りが設定値より小さい場合そちらを採用
                    received_data = client_socket.recv(min(remaining, self.body_bytes))
                    remaining -= len(received_data)
                    body_data += received_data
                print(
                    f"動画データの受信完了しました。動画データのサイズ: {len(body_data)} bytes"
                )

                # ボディデータを解析
                json_data, media_type, payload_data = unpack_mmp_message(
                    body_data, json_size, media_type_size, payload_size
                )
                # デバッグ
                print(f"json_data: {json_data}")
                print(f"media_type: {media_type}")
                print(f"payload_data: {len(payload_data)}")

                # 動画データを確認して問題が無ければ、ffmpegを使用してバイナリデータから動画ファイルに変換して保存する
                if not payload_data:
                    print(
                        f"動画データが存在していません。クライアント:{client_address}とのソケットを閉じます"
                    )
                    client_socket.close()
                else:
                    uploaded_file_path: str = "./output/output.mp4"
                    if decode_and_save_video(payload_data, uploaded_file_path):
                        # 動画ファイルに対する処理内容を確認して処理する
                        if json_data.get("action") == "1":
                            # 動画ファイルの自動圧縮
                            uploaded_processed_file_path = (
                                "./output/output_compressed.mp4"
                            )
                            if compress_video_file(
                                uploaded_file_path,
                                json_data.get("quality"),
                                uploaded_processed_file_path,
                            ):
                                status = "success"
                            else:
                                status = "failure"
                        elif json_data.get("action") == "2":
                            # 動画の解像度変更
                            uploaded_processed_file_path = "./output/output_resized.mp4"
                            if resize_video_resolution(
                                uploaded_file_path,
                                json_data.get("resolution"),
                                uploaded_processed_file_path,
                            ):
                                status = "success"
                            else:
                                status = "failure"
                        elif json_data.get("action") == "3":
                            # 動画のアスペクト比変更
                            uploaded_processed_file_path = (
                                "./output/output_aspect_ratio.mp4"
                            )
                            if change_video_aspect_ratio(
                                uploaded_file_path,
                                json_data.get("aspect_ratio"),
                                uploaded_processed_file_path,
                                json_data.get("fit_mode"),
                            ):
                                status = "success"
                            else:
                                status = "failure"
                        elif json_data.get("action") == "4":
                            # mp4ファイルをmp3ファイルに変換
                            uploaded_processed_file_path = "./output/output.mp3"
                            if convert_to_mp3file(
                                uploaded_file_path,
                                uploaded_processed_file_path,
                                media_type,
                            ):
                                status = "success"
                            else:
                                status = "failure"
                        elif json_data.get("action") == "5":
                            # 動画を切り取る
                            uploaded_processed_file_path = (
                                "./output/output_trimmed.gif"
                                if json_data.get("trim") == "gif"
                                else "./output/output_trimmed.webm"
                            )
                            if trim_video_to_gif_webm(
                                uploaded_file_path,
                                json_data.get("start_time"),
                                json_data.get("duration"),
                                uploaded_processed_file_path,
                                json_data.get("trim"),
                            ):
                                status = "success"
                            else:
                                status = "failure"

                # レスポンスを返す
                # 動画データ
                if status == "success":
                    with open(uploaded_processed_file_path, "rb") as f:
                        response_file_data = f.read()
                    # ファイルタイプデータ
                    response_file_type = media_type
                    # jsonデータ
                    response_json_data = {
                        "status_id": "200",
                        "file_name": uploaded_processed_file_path.split("/")[-1],
                    }
                elif status == "failure":
                    response_file_data = b""
                    response_file_type = "0"
                    response_json_data = {
                        "status_id": "400",
                        "message": "エラーが発生しました。以下の解決方法を参考にしてください。",
                        "solution": "動画データを確認してください。設定値を確認してください。",
                    }

                # レスポンスデータのヘッダーとボディデータを作成
                response_data = pack_mmp_message(
                    response_json_data, response_file_type, response_file_data
                )
                # レスポンスデータを送信
                client_socket.sendall(response_data)
                print("レスポンスを返しました")
                print("ソケットを閉じます")
                client_socket.close()

                # サーバーに一時動画したファイルを削除する
                if os.path.exists(uploaded_file_path):
                    os.remove(uploaded_file_path)
                if os.path.exists(uploaded_processed_file_path):
                    os.remove(uploaded_processed_file_path)
                print("動画ファイルを削除しました")

        except KeyboardInterrupt:
            print("ctrl + c 操作を受け付けました")
            self.server_running = False
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            self.server_running = False
        finally:
            # TCPサーバー閉じる
            self.tcp_socket.close()

    def response_data(self, _client_socket):
        """レスポンスを返す
        構成：
        最大16バイト
        ステータスコード（1バイト）+ メッセージ（可変長） 0でパディングされる
        """
        # メッセージを設定
        message = "success"
        message_bytes = message.encode("utf-8")
        # 設計する
        response = bytearray(16)
        response[0] = len(message_bytes)
        response[1 : 1 + len(message_bytes)] = message_bytes
        # 送信
        _client_socket.sendall(response)


if __name__ == "__main__":
    server = Server()
    server.server_start()
