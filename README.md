# EgoisticLilyPy

AutoEncoderモデルを採用したかな漢字変換エンジンです。  
iBus と連携させる ibus-egoisticlily はこちらにあります。  

https://github.com/syutadeveloper/ibus-egoisticlily  

## 起動方法

```shell script
egoisticlily -m model -p 50055
```

* -m : モデルパス
* -p : ポート番号

## 注意書き
Python版のEgoisticLilyです。 C++版は別途作成します。  
本コードでは、学習用コード及び、簡易版EgoisticLily（主に動作確認用）GRPCサーバーが同梱されています  

