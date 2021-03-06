RsServoManager
======================
RsServoManagerは双葉電子工業（株）のコマンド方式サーボである[RSシリーズ][rs]を
制御するRTコンポーネントです    
[G-ROBOTS][grobots]などに使用されているコントローラRPU11,[RPU10][rpu10]にも対応しています  
Python Moduleを使用した階層構造によりユーザー自身で改変が行いやすくなっています  
また、使用するサーボモータの個数などを個別の事例に合わせて簡単に設定できます   

[rs]: http://www.futaba.co.jp/robot/command_type_servos/index.html   
[grobots]: http://www.hpirobot.jp/index.html
[rpu10]: http://www.futaba.co.jp/robot/robot_processing_unit/index.html  

動作確認環境
------
Python:  
2.6.6  

pySerial:  
2.6(2003-2010)まで対応  

OS:  
Windows 7 64bit / 32bit  
Ubuntu 10.04 LTS / 12.04 LTS 32bit  

Servo:
RS301, 302, 303, 405 

Serial:
RSC-U485

ファイル構成
------
RsServoManager
│―RsServoManager.py  
│―pyrs.py  
│―ini   
│　　│―rsservomanager.ini    
│  
│―rtc.conf  

* RsServoManager.py  
RTC本体です  
* pyrs.py  
サーボモータを制御するPython Moduleです  
このモジュールは付属しますが、[こちら][pyprs]でも配布されています   
[pyprs]: https://github.com/HiroakiMatsuda/pyrs  
 
* rsservomanager.ini  
サーボモータの個数や指令値のリミットなどを設定します  
* rtc.conf  
ポートの設定や動作周期を設定できます  

注:本RTCにおいてユーザーが操作すると想定しているファイルのみ説明しています  

ファイルの設定はiniファイルを通して行えるので、簡単に設定を変えられます  
iniファイルはActivate時に読み込まれるので、設定を変更した場合は一度Deactivateしたあとに再度Activateすることで変更されます  


RTCの構成
------  
<img src="https://github.com/downloads/HiroakiMatsuda/RsServoManager/readme_01.png" width="400px" />    
データポートは3つあり、以下のようになっています  
  
* motion port :InPort  
データ型; TimedLongSeq   
[Flag, Id, Position, Time]  
 ・  `Flag` :  モーションの同期用フラグ  
0:同期なし  
1:同期あり  
Flagを1にすると設定したサーボモータ全てに同時に指令を送ります  
同期モードの場合は、サーボモータの個数分データが取得するまで移動しません  
 ・  `Id` :  サーボID  
指令を送るサーボモータのIDを指定します。IDは1~127の間で指定する必要があります    
 ・  `Position` :  移動位置  
サーボモータへ角度 [0.1 deg]を指定します   
 ・  `Time` :  移動時間  
指定位置までの移動時間 0~16383 [msec]の間で指定します  

* on_off port :InPort  
データ型; TimedLongSeq  
[Flag, Id, Torque mode]  
 ・  `Flag` :  モーションの同期用フラグ  
0:同期なし  
1:同期あり  
Flagを1にすると設定したサーボモータ全てに同時に指令を送ります  
同期モードの場合は、サーボモータの個数分データが取得するまで移動しません  
 ・  `Id` :  サーボID  
指令を送るサーボモータのIDを指定します。IDは1~127の間で指定する必要があります    
 ・  `Toruque mode` :  トルクモード指定  
0:トルクをオフにします  
1:トルクをオンにします  
2:ブレーキモードにします  
 
* sensor port :OutPort  
データ型; TimedLongSeq  
[Id, Angle, Time, Speed, Load, Temperature, Voltage]  
 ・  `'Angle` :  現在位置 [0.1 deg]  
 ・  `'Time` :  現在時間 [0.1 sec]  
現在時間はサーボが指令を受信し、移動を開始してからの経過時間です   
 ・  `'Speed` :  現在スピード [deg / sec]  
現在の回転スピードを取得できますが、この値は目安です。  
 ・  `'Load` :  現在負荷 [mA]  
サーボに供給されている電流を返しますが、この値は目安です。  
 ・  `Tempreture` :  現在温度 [degree celsius]  
この値はセンサの個体差により±3 [degree celsius] 程度の誤差があります  
 ・  `'Voltage` :  現在電圧 [10 mV]  
この値はセンサの個体差により±0.3 [V]程度の誤差があります    
  

使い方：　RsMotionを使用してテストする
------
###1. pySerialをインストールする###
pyrsは[pySerial](:http://pyserial.sourceforge.net/)を使用してシリアル通信を行なっています。  
pySerialがインストールされていない場合は、インストールしてから実行して下さい  

###2. 使用するサーボモータの設定する###
rsservomanager.iniをテキストエディタなどで開き編集します  

**[PORT]**  
  ・ ```port = XXX```  
使用するシリアルポートの設定をします  
WindowsではCOM1、Ubuntuでは/def/ttyUSB0のように入力します  
  ・ ```baudrate = X```  
ボーレートを設定します。RSシリーズでは通常115200 [bi/sec]となっています  
  ・ ```mode = XXX```  
動作モードを設定します  
RPU: RPU10, RPU11を使用する場合    
NORMAL: それ以外のコントローラ、シリアル変換器を使用する場合  

**[SERVO]**  
  ・ ```servo_num = X```  
使用するサーボモータの数を設定をします  
  ・ ``write_sens = X```  
ON:センサ出力有り  
OFF:センサ出力なし  
センサ出力を行うか設定します。サーボモータの数が多い場合はOFFすることで処理速度が改善される場合があります

以下の設定は使用するサーボモータの分だけ繰り返してください  
 ・ ``id_1 = X```  
使用するサーボモータのIDを指定します  
4つのサーボモータを使用する場合は、id1からid4まで設定します  
この際にid_は1から連続した値を指定してください  

**[POSITION]**  
  ・ ```min = X```  
使用するサーボモータの位置指令の最小値を設定をします  
  ・ ```max = X```  
使用するサーボモータの位置指令の最大値を設定をします  
  ・ ```offset = X```  
位置指令のオフセット値を指定します。RSシリーズは正負の値を持ちますが、
正の値のみで表現されているデータを使用するときなどに、
RSシリーズに合わせて値をオフセットする場合に設定します。
通常は0を指定してください  
 
###2. サーボモータ制御用RTCと接続する###
1. RsServoManager.py起動する  
ダブルクリックするなどして起動してください  
2. 指令値送信用RTC、RsMotionを起動する    
サーボモータ制御用RTCである[RsMotion][rsmotion]と接続します 
RsMotionは[ここ][rsmotion]からDLしてください   

[rsmotion]: https://github.com/HiroakiMatsuda/RsMotion
  
###3. サーボモータを動かす###
1. トルク保持命令を発行する  
下図のGUIのボタンを押すとサーボのトルク保持命令が発行されます  
緑のときにトルクON、赤のときにトルクOFFとなります  
一番上のボタンは全サーボモータにトルク保持命令を発行します    
<img src="https://github.com/downloads/HiroakiMatsuda/RsMotion/readme_03.png" width="400px" />  
<img src="https://github.com/downloads/HiroakiMatsuda/RsMotion/readme_04.png" width="400px" />        

2. サーボモータの移動指令を発行する  
各スライダーバーを動かすことでサーボモータに移動指令を発行できます  
<img src="https://github.com/downloads/HiroakiMatsuda/RsMotion/readme_05.png" width="400px" />    

3. 現在のセンサ値を確認する
GUIの右側のテキストボックスにはサーボのセンサ値が表示されています  
      
以上が本RTCの使い方となります  

ライセンス
----------
Copyright &copy; 2012 Hiroaki Matsuda  
Licensed under the [Apache License, Version 2.0][Apache]  
Distributed under the [MIT License][mit].  
Dual licensed under the [MIT license][MIT] and [GPL license][GPL].  
 
[Apache]: http://www.apache.org/licenses/LICENSE-2.0
[MIT]: http://www.opensource.org/licenses/mit-license.php
[GPL]: http://www.gnu.org/licenses/gpl.html