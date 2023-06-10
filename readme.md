# Raspberry Pi Pico
raspberry pi picoを利用した工作プログラム

- 気温・湿度・気圧の表示ツール
- 自動運転車

## How to use
1. ブートモードでUF2ファイルを書き込む
2. secret.pyを作成する
3. `src/`を書き込む
4. 利用するプログラムを`main.py`として書き込む
5. 必要に応じてパッケージ(`lib/`)を追加
6. `main.py`を実行

## Examples
### 気温・湿度・気圧の表示ツール
| 回路図 | 画像 |
| --- | --- |
| ![回路図](./examples/temperature_humidity_pressure/circuit.png) | ![画像](./examples/temperature_humidity_pressure/image.jpeg) |

### 自動運転車
| 回路図 | 画像 |
| --- | --- |
| ![回路図](./examples/robot_car/circuit.png) | ![画像](./examples/robot_car/image.jpeg) |

https://github.com/eycjur/raspberry_pi/assets/63308909/99cbded5-7447-4c20-84a9-49963bdfbd97

## Todo
- 前輪を左右独立に動くようにする
- 強化学習ロジックを組み込む
- 位置情報を取得して目的地まで自動運転する
- カメラで画像認識をする
- ゴミの吸い取り機能を追加してお掃除ロボット化

## Reference
- [【Raspberry Pi Pico】自動運転ロボットカーの製作　②回路・プログラム編](https://hellobreak.net/raspberry-pi-pico-auto-robot-car2/)
