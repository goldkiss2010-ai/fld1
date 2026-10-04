![FLD1 — Fields, concisely.](branding/key-visual.jpg)

# FLD1 — 粒子の状態を制作環境へ渡す

**状態を保存し、観察と表現をDCCで続ける。**

FLD1は位置・微分・visibility・汎用スカラーを一定間隔で保存する実験的なバイナリ形式です。
生成言語やバックエンドは固定しません。数式、数値シミュレーション、画像由来の点群、
独自の手続き生成を、共通の状態として受け渡します。Pythonは付属参照ツールの実装言語です。

[固定規約](docs/contract-v1.md) · [バイト配置](docs/format.md) · [設計思想](docs/design.md) · [今後の検討](docs/roadmap.md)

## 固定するもの

基本プロファイルは`point3-pv`。右手系XYZ・Z上向き、全サンプルで粒子数と順序を固定します。
各粒子は`x y z vx vy vz visibility scalar0`の8個のfloat32、ヘッダーは32バイトです。

新規の基本規約は保存サンプル番号q=0,1,2,…、sample_rate=1、微分はdx/dqです。
絶対的な映像上の時間尺度を固定せず、DCC側でq=g(t)を決めます。
補間、配置、カメラ、投影、点の大きさ、色、合成も受け取り側の機能です。
visibilityの重みをどう描画へ反映するかは、受け取り側が決めます。

参照読取実装は旧sample_rateも扱います。normalize_cache.pyで保存位置とHermite補間曲線を保ち、
微分を旧sample_rateで割ってサンプル番号基準に換算できます。再生設定も対応して変更してください。
速度に依存する明るさやストリークは、数値の換算で見た目が変わる場合があります。

## 小さく試す

Python 3.10以降で、リポジトリ直下から実行します。外部ライブラリは不要です。

```sh
python examples/make_orbit.py --output orbit-legacy.fld1 --count 128
python normalize_cache.py orbit-legacy.fld1 orbit.fld1
python examples/inspect_cache.py orbit.fld1 --frame 12
python -m unittest discover -s tests -v
```

円運動の例は旧sample_rate=12で書き出すため、続けて換算します。流体シミュレーションではありません。
参照実装は理解と照合のための最小例です。数百万粒子では、生成側で連続配列の一括入出力を使えます。
読取時にはヘッダー・stride・ファイルサイズを検査します。各レコードの値域は生成側の責任です。

## 二つのリポジトリ

このリポジトリで思想、仕様、規約、読み書き例、将来の拡張案を管理します。
[AE Handoff](https://github.com/goldkiss2010-ai/ae-handoff)では、AEプラグイン、粒子場生成コード、
設定、作例を管理します。参照ツールはcore/に実体を収録し、追加のサブモジュール取得は不要です。
AEプラグインのソース・ビルド設定・開発履歴は非公開で維持し、ビルド済みプラグイン、
使い方、粒子場、生成コードを配布する方針です。FLD1仕様・参照ツールはこちらで提供します。

メッシュ、可変粒子数、不連続、任意の追加属性などはv1には含めません。
FLD2や別プロファイルは必要性を確認してから設計し、v1の意味とバイト配置は後から変更しません。