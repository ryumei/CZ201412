
# 事前準備

Redmine へのアクセスに [python-remine](http://python-redmine.readthedocs.org/) を、
出力のテンプレートエンジンに [jinja2](http://jinja.pocoo.org/) を利用しています。

    $ easy_install python-redmine jinja2

# 設定ファイルの配置

    $ mv sample.conf.json conf.json

Edit ``conf.json``

# 実行例

    $ python summary_redmines.py > output.html

## 動作確認環境

Python 3.3
