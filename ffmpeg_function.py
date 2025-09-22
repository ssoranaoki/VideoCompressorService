import os
import subprocess


def decode_and_save_video(video_data: bytes, output_path: str) -> bool:
    """バイナリデータをffmpegでデコードして動画ファイルとして保存する"""
    try:
        # outputディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                "pipe:0",
                "-c",
                "copy",
                "-f",
                "mp4",
                output_path,
            ],
            input=video_data,
            capture_output=True,
        )

        if result.returncode == 0:
            print(f"保存成功: {output_path}")
            return True
        else:
            print(
                f"decode_and_save_video関数でffmpegエラーが発生しました: {result.stderr.decode('utf-8', errors='ignore')}"
            )
            return False

    except Exception as e:
        print(f"decode_and_save_video関数でエラーが発生しました: {e}")
        return False


def compress_video_file(input_path: str, crf_number: str, output_path: str) -> bool:
    """ファイルパスを指定して動画を圧縮する"""
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-vcodec",
                "libx264",
                "-crf",
                crf_number,
                "-preset",
                "medium",
                "-tune",
                "film",
                "-an",  # 音声を削除
                "-f",
                "mp4",
                output_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"圧縮成功: {output_path}")
            return True
        else:
            print(f"compress_video_file関数でffmpegエラーが発生しました: {result.stderr}")
            return False

    except Exception as e:
        print(f"compress_video_file関数でエラーが発生しました: {e}")
        return False


def convert_to_mp3file(input_path: str, output_path: str, target_format: str) -> bool:
    """動画フォーマットを変換する"""
    try:
        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-c",
                "copy",
                "-f",
                target_format,
                output_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"フォーマット変換成功: {output_path}")
            return True
        else:
            print("ffmpegエラー")
            return False

    except Exception as e:
        print(f"convert_video_format関数でエラーが発生しました: {e}")
        return False


def trim_video_to_gif_webm(
    input_path: str,
    start_time: str,
    duration: str,
    output_path: str,
    output_format: str,
) -> bool:
    """時間範囲を指定して動画を切り取り、GIFまたはWEBMフォーマットに変換する

    Args:
        input_path: 入力動画ファイルのパス
        start_time: 開始時間 (例: "00:00:10" または "10")
        duration: 切り取り時間の長さ (例: "00:00:05" または "5")
        output_path: 出力ファイルのパス
        output_format: 出力フォーマット ("gif" または "webm")

    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # outputディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if output_format.lower() == "gif":
            # GIF変換用のffmpegコマンド
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-ss",
                    start_time,
                    "-t",
                    duration,
                    "-vf",
                    "fps=10,scale=320:-1:flags=lanczos",
                    "-c:v",
                    "gif",
                    "-y",  # 既存ファイルを上書き
                    output_path,
                ],
                capture_output=True,
                text=True,
            )
        elif output_format.lower() == "webm":
            # WEBM変換用のffmpegコマンド
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-ss",
                    start_time,
                    "-t",
                    duration,
                    "-c:v",
                    "libvpx-vp9",
                    "-crf",
                    "30",
                    "-b:v",
                    "0",
                    "-an",  # 音声を削除
                    "-y",  # 既存ファイルを上書き
                    output_path,
                ],
                capture_output=True,
                text=True,
            )
        else:
            print(f"サポートされていないフォーマット: {output_format}")
            return False

        if result.returncode == 0:
            print(f"動画切り取り・変換成功: {output_path}")
            return True
        else:
            print(
                f"trim_video_to_gif_webm関数でffmpegエラーが発生しました: {result.stderr}"
            )
            return False

    except Exception as e:
        print(f"trim_video_to_gif_webm関数でエラーが発生しました: {e}")
        return False


def resize_video_resolution(input_path: str, resolution: str, output_path: str) -> bool:
    """動画の解像度を変更する"""
    try:
        # outputディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if resolution == "1":
            width = 1920
            height = 1080
        elif resolution == "2":
            width = 1280
            height = 720
        elif resolution == "3":
            width = 640
            height = 480
        elif resolution == "4":
            width = 320
            height = 240

        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-vf",
                f"scale={width}:{height}",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "copy",
                "-f",
                "mp4",
                output_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"解像度変更成功: {output_path} ({width}x{height})")
            return True
        else:
            print(
                f"resize_video_resolution関数でffmpegエラーが発生しました: {result.stderr}"
            )
            return False

    except Exception as e:
        print(f"resize_video_resolution関数でエラーが発生しました: {e}")
        return False


def change_video_aspect_ratio(
    input_path: str, aspect_ratio: str, output_path: str, fit_mode: str
) -> bool:
    """動画のアスペクト比を変更する

    Args:
        input_path: 入力動画ファイルパス
        aspect_ratio: 目標アスペクト比 ("16:9", "4:3", "1:1" など)
        output_path: 出力動画ファイルパス
        fit_mode: フィット方法
            - "letterbox": 元の映像を維持し、余白を黒で埋める
            - "crop": 元の映像をクロップして目標アスペクト比に合わせる
            - "stretch": 元の映像を引き延ばして目標アスペクト比に合わせる
    """

    if aspect_ratio == "1":
        width_ratio = 16
        height_ratio = 9
    elif aspect_ratio == "2":
        width_ratio = 4
        height_ratio = 3
    elif aspect_ratio == "3":
        width_ratio = 1
        height_ratio = 1

    try:
        # outputディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # アスペクト比を計算
        target_aspect = float(width_ratio) / float(height_ratio)

        if fit_mode == "1":
            # letterbox: 元の映像を維持し、余白を黒で埋める
            scale_filter = f"scale=iw*min(1\\,if(sar\\,1/sar\\,1)*{target_aspect}/dar):ih*min(1\\,dar/({target_aspect}*if(sar\\,sar\\,1))),pad=iw*{target_aspect}/dar:ih:x=(ow-iw)/2:y=(oh-ih)/2:color=black"
        elif fit_mode == "2":
            # crop: 元の映像をクロップして目標アスペクト比に合わせる
            scale_filter = f"scale=iw*max(1\\,if(sar\\,1/sar\\,1)*{target_aspect}/dar):ih*max(1\\,dar/({target_aspect}*if(sar\\,sar\\,1))),crop=iw*{target_aspect}/dar:ih"
        elif fit_mode == "3":
            # stretch: 元の映像を引き延ばして目標アスペクト比に合わせる
            scale_filter = f"scale=iw:ih,setsar={aspect_ratio}"
        else:
            print(
                f"不正なfit_mode: {fit_mode}. 'letterbox', 'crop', 'stretch'のいずれかを指定してください"
            )
            return False

        result = subprocess.run(
            [
                "ffmpeg",
                "-i",
                input_path,
                "-vf",
                scale_filter,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-c:a",
                "copy",
                "-f",
                "mp4",
                output_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(
                f"アスペクト比変更成功: {output_path} (アスペクト比: {aspect_ratio}, モード: {fit_mode})"
            )
            return True
        else:
            print(
                f"change_video_aspect_ratio関数でffmpegエラーが発生しました: {result.stderr}"
            )
            return False

    except Exception as e:
        print(f"change_video_aspect_ratio関数でエラーが発生しました: {e}")
        return False
