import os
import socket

from dotenv import load_dotenv

from custom_protocol import pack_mmp_message, unpack_mmp_message

# 環境変数を読み込む
load_dotenv()


class Client:
    def __init__(self) -> None:
        # バッファサイズ
        self.header_bytes: int = int(os.getenv("header_bytes", 8))
        self.body_bytes: int = int(os.getenv("body_bytes", 1400))
        self.port: int = int(os.getenv("port", 8888))
        self.ip: str = os.getenv("ip", "127.0.0.1")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """サーバーに接続する"""
        print("サーバーに接続中です....")
        self.socket.connect((self.ip, self.port))

    def send_and_recieve_processing(self):
        """送信と受信の処理"""

        # ファイルパスの取得
        print("ファイルのパスを入力してください")
        while True:
            # file_path = input()
            file_path = "Azki.mp4"  # デバッグ
            # ファイル読み込み
            with open(file_path, "rb") as f:
                file_data = f.read()
            # ファイルサイズが4GB以上の場合エラー
            if len(file_data) > 4 * 1024 * 1024 * 1024:
                print("ファイルサイズが4GBを超えています。別のファイルを選んでください")
            else:
                break

        # ファイルの拡張子入力
        print("ファイルの拡張子を入力してください")
        while True:
            # file_extension = input()
            file_extension = "mp4"  # デバッグ
            # ファイル拡張子の整合性確認
            if not file_path.endswith(file_extension):
                print(
                    f"入力した値:{file_extension} とファイルの拡張子が違います。再度入力してください。"
                )
            else:
                break

        # 操作内容を表示
        operation_list = {
            "1": "Compress Video",
            "2": "Change Resolution",
            "3": "Change Aspect Ratio",
            "4": "Extract Audio",
            "5": "Trim Video",
        }
        print("操作内容:")
        for key, value in operation_list.items():
            print(f"{key}: {value}")
        # 操作内容を入力
        print("操作内容の数字を入力してください")
        while True:
            operation = input()
            # 操作内容の整合性確認
            if operation not in operation_list:
                print(f"入力した値:{operation}が不正です。再度入力してください。")
            else:
                break

        # 処理の引数を含むボディデータのjsonを作成
        json_data = {"action": operation}

        while True:
            # 操作内容に応じて必要な要件を入力してjsonデータに追加する
            if operation == "1":
                print(
                    "エンコード時の品質設定値を0~51の間で入力してください。おすすめ値は23です。"
                )
                quality = input()
                if quality:
                    json_data["quality"] = quality
                    break
                else:
                    print("未入力は認めれません。再度入力してください。")
            elif operation == "2":
                print("変更したい解像度を選択してください。")
                print("1: 1920x1080")
                print("2: 1280x720")
                print("3: 640x480")
                print("4: 320x240")
                resolution = input()
                if resolution:
                    json_data["resolution"] = resolution
                    break
                else:
                    print("未入力は認めれません。再度入力してください。")
            elif operation == "3":
                print("変更したいアスペクト比を入力してください。")
                print("1: 16:9")
                print("2: 4:3")
                print("3: 1:1")
                aspect_ratio = input()
                print("フィット方法を入力してください。")
                print("1: letterbox")
                print("2: crop")
                print("3: stretch")
                fit_mode = input()
                if aspect_ratio and fit_mode:
                    json_data["aspect_ratio"] = aspect_ratio
                    json_data["fit_mode"] = fit_mode
                    break
                else:
                    print("未入力は認めれません。再度入力してください。")
            elif operation == "4":
                break
            elif operation == "5":
                print("GIFまたはWEBMに変換します。どちらかを入力してください。")
                trim = input().lower()
                print("切り取りを開始する動画の時間を入力してください。")
                print("例: 00:00:10 または 10")
                start_time = input()
                print("切り取りを終了する動画の時間を入力してください。")
                print("例: 00:00:10 または 10")
                duration = input()
                if trim and start_time and duration:
                    json_data["trim"] = trim
                    json_data["start_time"] = start_time
                    json_data["duration"] = duration
                    break
                else:
                    print("未入力は認めれません。再度入力してください。")

        # サーバーへ送信
        send_data = pack_mmp_message(json_data, file_extension, file_data)
        print(f"send_data: {len(send_data)}")
        self.socket.sendall(send_data)

        # ヘッダーを取得
        header_data_bytes = self.socket.recv(self.header_bytes)
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
            received_data = self.socket.recv(min(remaining, self.body_bytes))
            remaining -= len(received_data)
            body_data += received_data
        print(f"動画データの受信完了しました。動画データのサイズ: {len(body_data)} bytes")

        # ボディデータを解析
        json_data, media_type, payload_data = unpack_mmp_message(
            body_data, json_size, media_type_size, payload_size
        )
        # デバッグ
        print(f"json_data: {json_data}")
        print(f"media_type: {media_type}")
        print(f"payload_data: {len(payload_data)}")

        if json_data.get("status_id") == "200":
            # 受信したバイナリデータから動画を作成して保存
            output_file_path = f"./client_received_data/{json_data.get('file_name')}"
            with open(output_file_path, "wb") as f:
                f.write(payload_data)
        elif json_data.get("status_id") == "400":
            print(json_data.get("message"))
            print(json_data.get("solution"))

        # ソケットを閉じる
        self.socket.close()

    def run(self):
        """メイン処理"""
        try:
            # サーバー接続
            self.connect()
            # 送信と受信処理
            self.send_and_recieve_processing()
        except KeyboardInterrupt:
            print("ctrl + c 操作を受け付けました")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            print("プログラムを終了します。")
        finally:
            self.socket.close()


if __name__ == "__main__":
    client = Client()
    client.run()
