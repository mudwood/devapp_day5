# devapp_day5
デベロッパーアプリケーションコース day5

# 構成
*.sh ... 各simを起動するスクリプト（各vehicle用のSYSIDと初期位置が設定してある）
*.txt ... 各vehicle用wpファイル（MPから出力）
automove.py ... 本体

# 初期設定
各ファイルを任意のディレクトリに保存する。
(15期の導入マニュアル通りであれば /home/ardupilot/ardupilot/dev-app/day5 が望ましい）
上のディレクトリ以外であれば、automove.pyのl.283～292にWPファイルのパスがあるので修正する。

# 実行
１．1_???? ～ 5_??? のスクリプトを起動
２．MPを起動、14550～14590 の５つを接続
３．automove.py を実行
