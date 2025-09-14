import socket


class Client:
    def __init__(self) -> None:
        # バッファサイズ
        self.header_bytes = 32
        self.body_bytes = 1400
        self.port = 8888
        self.ip = "127.0.0.1"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """サーバーに接続する"""
        print("サーバーに接続中です....")
        self.socket.connect((self.ip, self.port))

    def send_and_recieve_processing(self):
        """送信と受信の処理"""
        # ファイルパスの取得
        file_path = input("ファイルのパスを入力してください:")
        # mp4確認
        if not file_path.endswith(".mp4"):
            print("拡張子がmp4ではありません。")
            print("プログラムを終了します。再度実行してください。")
            self.socket.close()
        # ファイル読み込み
        with open(file_path, "rb") as f:
            file_data = f.read()
        # ファイルサイズが4GB以上あるか確認
        if len(file_data) > 4 * 1024 * 1024 * 1024:
            print("ファイルサイズが4GBを超えています。")
            print("プログラムを終了します。再度実行してください。")
            self.socket.close()

        # ファイル送信
        # ヘッダー32バイト、ボディ1400バイト送信する設計
        # ヘッダーにはデータファイルの長さを格納
        # ボディにはデータファイルのデータを格納
        header = len(file_data).to_bytes(32, byteorder="big")
        remaining = len(file_data)
        total_sent = 0
        # ヘッダー送信
        self.socket.sendall(header)
        while remaining > 0:
            # 効率よく送信するため送信データの残りが設定値より小さい場合そちらを採用
            chunk = file_data[total_sent : total_sent + min(remaining, self.body_bytes)]
            self.socket.sendall(chunk)
            total_sent += len(chunk)
            remaining -= len(chunk)
        print("ファイル送信完了しました")
        print(f"ファイルサイズ: {total_sent} bytes")

        # サーバーからの応答受信
        recieved_data = self.socket.recv(16)
        print(f"受信データ: {recieved_data}")
        # 規格エラー
        if len(recieved_data) != 16:
            print("受信データが16バイトではありません")
            self.socket.close()
            return

        # 受信データから内容を取得
        status_length = recieved_data[0]
        status_bytes = recieved_data[1 : 1 + status_length]
        # パディングされている場合を考慮して0を取り除く
        status = status_bytes.decode("utf-8").rstrip("\x00")
        print(f"ステータス: {status}")

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