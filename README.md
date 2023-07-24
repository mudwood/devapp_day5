# devapp_day5
デベロッパーアプリケーションコース day5

# 構成
*.sh ... 各simを起動するスクリプト（各vehicle用のSYSIDと初期位置が設定してある）<br>
*.txt ... 各vehicle用wpファイル（MPから出力）<br>
automove.py ... 本体<br>

# 初期設定
各ファイルを任意のディレクトリに保存する。<br>
(15期の導入マニュアル通りであれば /home/ardupilot/ardupilot/dev-app/day5 が望ましい）<br>
上のディレクトリ以外であれば、automove.pyのl.283～292にWPファイルのパスがあるので修正する。<br>

# 実行
１．1_???? ～ 5_??? のスクリプトを起動<br>
２．MPを起動、14550～14590 の５つを接続<br>
３．automove.py を実行<br>

# そのた
automove.py の最終、l.294かl.295のいずれかを実行するように選択する
