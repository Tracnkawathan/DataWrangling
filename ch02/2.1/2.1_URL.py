### 2.1 データ分析の例：短縮URL 1.usa.govへの変換データ

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# path of 'usagov' txt.
path = 'bitly/usagov_bitly_data2013-03-15-1363313968.txt'
# read a line of the txt file.
open(path).readline()

# now we are going to read in json style.
import json
# path of 'usagov' txt, again.
path = 'bitly/usagov_bitly_data2013-03-15-1363313968.txt'
# リスト内包によってtxt各行をリードして、そのままpythonディクショナリ型を作成
records = [json.loads(line) for line in open(path)]

# let's take a look of the indices of the list.
records[0]

# 0の中の、tzという属性を見る場合、後ろに属性の名前を書いて対応する値を読み出せる。
# ちなみに、tzはtime zone の略とのこと。出力にある'u'は'unicode'のu.
records[0]['tz']
records[0]['ll']

# printをつかって出力すれば、関数の戻り値が出力されるので、uはでてこない。
print records[0]['tz']

### 2.1.1. Python標準機能を使用したタイムゾーン情報の集計

# 先ほどのリスト内包を使って、タイムゾーンリストを抽出してみる。が、エラーになる。。。
# KeyError: 'tz'と書いてあるから、途中で'tz'が見つからなかたのだろう。
# 全行に'tz'があるわけではなさそう。。

#time_zones = [rec['tz'] for rec in records]

# 実は、リスト内包には条件文も加えられるので、便利。
# 条件文を追加したければ、後ろに'if'をつけるだけ。
time_zones = [rec['tz'] for rec in records  if 'tz' in rec]
#time_zonesの先頭10行をみる。
time_zones[:10]

#それぞれのタイムゾーンがいくつ出てくるか、回数をまとめてみる
#方法1.python標準ライブラリ、方法2.Pandas があるが、
#まずは、方法1.
def get_counts(seq):
    counts = {}                 #{}は、辞書型。キーと値で1セット。
    for x in seq:               #seq内の各要素xに対して
        if x in counts:             #counts{}の中にすでにキー:xがあれば
            counts[x] += 1          #1足す
        else:                       #なければ
            counts[x] = 1           #1にする(キーの新規追加)
    return counts

#time_zonesのヒストグラムを作る
counts = get_counts(time_zones)
#NewYorkの数は...
counts['America/New_York']

#time_zonesの総要素数は、、、
len(time_zones)

#ここで、せっかくなので、Top 10を返す関数を定義する。
def top_counts(count_dict, n = 10):
    value_key_pairs = [(count, tz) for tz, count in count_dict.items()] #引数の辞書からペアのリストを再構成。ペアは(count, tz)の順で格納
    value_key_pairs.sort()  # 続いて、sort関数によってデータを並び替える。これはデフォルトで1軸で昇順にソートされる。
    return value_key_pairs[-n:] # 上位の結果として末尾から順に取り出したいので、インデックスに-n:を与えている。

#上位 10件を得られる
top_counts(counts)


### 2.1.2. pandasを使用したタイムゾーン情報の集計

# pandasのDataFrameを使ってみる。表形式データ。

#import
from pandas import DataFrame, Series
import pandas as pd
import numpy as np

#records をdataframe形式に変えてやる。
frame = DataFrame(records)
frame

#frame['tz']という記法で、imezoneデータだけを抽出したSeriesオブジェクトを作れる。ここでは10件表示する。
frame['tz'][:10]

#Seriesオブジェクトには value_countsメソッドがあり、これで上位10件を出せる。
tz_counts = frame['tz'].value_counts()
tz_counts[:10]

#fillnaで、タイムゾーン情報が存在していない箇所には'missing'を埋める
clean_tz = frame['tz'].fillna('missing')
#タイムゾーンはあるけど中身が空文字だった場合は、Unknownという文字列に置き換える
clean_tz[clean_tz == ''] = 'Unknown'

tz_counts = clean_tz.value_counts()
tz_counts[:10]

#matplotlibを使ってプロットする
%matplotlib inline

tz_counts[:10].plot(kind='barh', rot=0)

#今度は"a"のデータを見て見る。アクセス元のブラウザとか、機器とか、アプリの情報が入っている。
frame['a'][1]
frame['a'][50]
frame['a'][51]

#中身が複雑なので、ここでpython標準の文字列操作と正規表現を使ってみよう。
# frameの列aのうち、nanを落とした物の中の各要素xについて、スペースで分けたうちの一番最初の文字列を拾い、シリーズにする。
results = Series([x.split()[0] for x in frame.a.dropna()])

#できたシリーズの上から5つ
results[:5]

#できたシリーズの上位8つ
results.value_counts()[:8]

#Mozillaユーザか否かで文字列を分けてみよう。

#フレーム'a'のうち、存在しないレコードを削除する
cframe = frame[frame.a.notnull()]

#numpyのWhereをつかってMozillaかどうかを振り分け
#where(condition,x,y)により戻されるndarrayには、conditionが真の場合にはx,技の場合にはyが入る
#excelのif文っぽい挙動をして、新たなキーを作る感じか
operating_system = np.where(cframe['a'].str.contains('Mozilla'),'Mozilla','not Mozilla')

#pandasのgroupbyをつかって、cframeのレコードをタイムゾーンと稼働OSの組み合わせごとにグループ化する
by_tz_os = cframe.groupby(['tz', operating_system])

by_tz_os.head()
#groupbyで指定した因子のサイズを集計する。
by_tz_os.size().head()

agg_counts_1d = by_tz_os.size()
agg_counts_1d[:10]
#２個あるカテゴリをunstackでほどいて、1次元データを2次元データに置き換える。
agg_counts = by_tz_os.size().unstack().fillna(0)
agg_counts[:10]

#昇順のソートを使用する。Numpyのargsortで並べ替えできる
indexer = agg_counts.sum(1).argsort()
#indexerは2列目がキモ。69,77,24,...のインデックスがMozilla+NotMozillaの総数の少ない順に並んでいる。
indexer[:10]

#numpy takeは、要素をindexで抜き出すだけ
agg_counts.take([1])
agg_counts.take([2])
agg_counts.take([3])

#indexerで上位10件の項目を抜き出してsubsetを作る（多いのから10個分）
count_subset = agg_counts.take(indexer)[-10:]

#プロットする
count_subset.plot(kind='barh', stacked=True)

#divでMozillaとnot Mozillaの割合を出す
normed_subset = count_subset.div(count_subset.sum(1), axis=0)
normed_subset.plot(kind='barh', stacked=True)
