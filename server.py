import socket


class Server:
    def __init__(self):
        self.server_running = True
        # バッファサイズ
        self.header_bytes = 32
        self.body_bytes = 1400
        # TCP設定
        self.tcp_port = 8888
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
                print(f"{client_address} からの接続を受け入れました")

                header_data = client_socket.recv(self.header_bytes)
                file_size = int.from_bytes(header_data, byteorder="big")

                # 4GBの確認
                if file_size > 4 * 1024 * 1024 * 1024:
                    print("アップロードファイルの容量が4GBを超えています")
                    client_socket.close()

                # 動画データ受信
                # 設計として基本的に1400バイトずつ受信する
                body_data = b""
                remaining = file_size
                while remaining > 0:
                    # 効率よく受信するため受信データの残りが設定値より小さい場合そちらを採用
                    received_data = client_socket.recv(min(remaining, self.body_bytes))
                    remaining -= len(received_data)
                    body_data += received_data
                print("動画データの受信完了しました")
                print(f"動画データのサイズ: {len(body_data)} bytes")

                # レスポンスを返す
                self.response_data(client_socket)
                client_socket.close()

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