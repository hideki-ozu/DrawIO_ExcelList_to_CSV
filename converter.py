# 必要なライブラリのインポート
import csv  # CSVファイルの読み書きに使用
import pandas as pd # Excelファイルの読み書きに使用
from collections import defaultdict  # 初期値を持つ辞書型を使用するため
import sys  # コマンドライン引数の処理に使用
import tkinter as tk  # GUIの作成に使用
from tkinter import filedialog  # ファイル選択ダイアログに使用
import os  # ファイルパス操作に使用


def select_file(title="ファイルを選択", filetypes=(("Excelファイル", "*.xlsx;*.xls"), ("CSVファイル", "*.csv"), ("すべてのファイル", "*.*"))):
    """
    GUIでファイルを選択するためのダイアログを表示する関数
    
    Args:
        title (str): ダイアログのタイトル
        filetypes (tuple): 選択可能なファイルタイプのリスト
        
    Returns:
        str: 選択されたファイルのパス。キャンセルされた場合は空文字列
    """
    # tkinterのルートウィンドウを作成し、非表示にする
    root = tk.Tk()
    root.withdraw()
    
    # ファイル選択ダイアログを表示
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=filetypes
    )
    
    # ルートウィンドウを破棄
    root.destroy()
    
    return file_path

def select_save_file(title="保存先を選択", defaultextension=".csv", filetypes=(("CSVファイル", "*.csv"), ("すべてのファイル", "*.*"))):
    """
    GUIで保存先ファイルを選択するためのダイアログを表示する関数
    
    Args:
        title (str): ダイアログのタイトル
        defaultextension (str): デフォルトのファイル拡張子
        filetypes (tuple): 選択可能なファイルタイプのリスト
        
    Returns:
        str: 選択された保存先ファイルのパス。キャンセルされた場合は空文字列
    """
    # tkinterのルートウィンドウを作成し、非表示にする
    root = tk.Tk()
    root.withdraw()
    
    # ファイル保存ダイアログを表示
    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes
    )
    
    # ルートウィンドウを破棄
    root.destroy()
    
    return file_path

def convert_csv_to_custom_format(input_csv_path, output_csv_path):
    """
    入力CSVファイルをDraw.io用のカスタムフォーマットCSVに変換する関数
    
    Args:
        input_csv_path (str): 入力CSVファイルのパス
        output_csv_path (str): 出力CSVファイルのパス
    """
    # ノードデータを格納するための辞書を初期化
    # 各ノードに対して、接続情報や信号、高さなどの属性を保持する
    # ノードデータを格納するための辞書を初期化
    # 各ノードに対して、接続情報や信号、高さなどの属性を保持する
    node_data = defaultdict(lambda: {
        'outgoing_targets': [],  # 出力先ノードのリスト
        'outgoing_signals': [],  # 出力信号のリスト
        'incoming_targets': [],  # 入力元ノードのリスト
        'incoming_signals': [],  # 入力信号のリスト
        'incoming_count': 0,     # 入力接続の数
        'outgoing_count': 0,     # 出力接続の数
        'height': 0              # ノードの高さ（描画用）
    })

    try:
        # ファイルの拡張子を取得
        file_extension = os.path.splitext(input_csv_path)[1].lower()
        
        data_rows = []
        required_headers = ['From', 'Signal', 'Dist', 'To']

        # 拡張子に応じてファイルを読み込む
        if file_extension == '.csv':
            # CSVファイルを読み込む
            with open(input_csv_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                # 必要なヘッダーが存在するか確認
                if not reader.fieldnames or not all(f in reader.fieldnames for f in required_headers):
                    print(f"エラー: 入力CSV '{input_csv_path}' に必要なヘッダー（{', '.join(required_headers)}）がありません。")
                    return
                data_rows = list(reader) # イテレータをリストに変換
        elif file_extension in ['.xlsx', '.xls']:
            # Excelファイルを読み込む
            try:
                df = pd.read_excel(input_csv_path)
                # 必要なヘッダーが存在するか確認
                if not all(f in df.columns for f in required_headers):
                    print(f"エラー: 入力Excel '{input_csv_path}' に必要なヘッダー（{', '.join(required_headers)}）がありません。")
                    return
                # DataFrameを辞書のリストに変換
                data_rows = df.to_dict('records')
            except Exception as e:
                print(f"エラー: Excelファイル '{input_csv_path}' の読み込み中にエラーが発生しました: {e}")
                return
        else:
            # サポートされていないファイル形式の場合
            print(f"エラー: サポートされていないファイル形式です: {file_extension}")
            return

        # 読み込んだデータを処理
        for row in data_rows:
            # 各列の値を取得 (Excelの場合、数値として読み込まれる可能性を考慮し、strに変換)
            from_node = str(row.get('From', '')).strip()
            signal = str(row.get('Signal', '')).strip()
            dist = str(row.get('Dist', '')).strip()
            to_node = str(row.get('To', '')).strip()

            #signalが'nan'の場合は空文字に変換 （Excelからの読み込み時に発生する可能性がある）
            if signal == 'nan':
                signal = ''

            # いずれかの必須フィールドが空の場合はスキップ（またはエラー処理）
            #if not all([from_node, signal, dist, to_node]):
            #    print(f"警告: 必須フィールドが空の行をスキップしました: {row}")
            #    continue

            source = from_node
            target = to_node

            # 方向（OUT/IN）に基づいてノードデータを更新
            if dist.upper() == 'OUT':
                # OUTの場合：sourceからtargetへの出力接続
                node_data[source]['outgoing_targets'].append(target)
                node_data[source]['outgoing_signals'].append(signal)
                node_data[source]['outgoing_count'] += 1
                node_data[target]['incoming_count'] += 1
            elif dist.upper() == 'IN':
                # INの場合：sourceへのtargetからの入力接続
                node_data[source]['incoming_targets'].append(target)
                node_data[source]['incoming_signals'].append(signal)
                node_data[source]['incoming_count'] += 1
                node_data[target]['outgoing_count'] += 1
            else:
                # 不明な方向値の場合はスキップ
                print(f"警告: 不明なDist値 '{dist}' を含む行をスキップしました: {row}")
                continue

        # 各ノードの高さを計算
        # 高さは入力または出力接続の数（多い方）に基づいて決定
        for node in node_data:
            in_count = node_data[node]['incoming_count']
            out_count = node_data[node]['outgoing_count']
            # 高さは接続数に14を掛けた値（Draw.ioでの表示用）
            node_data[node]['height'] = max(in_count, out_count) * 14

        # 出力CSVのデータ行を準備
        output_rows = []
        
        # 各ノードの最大接続数と信号数を計算
        # これらの値は出力CSVのヘッダー作成に使用される
        max_targets_out = max((len(data['outgoing_targets']) for data in node_data.values()), default=0)
        max_signals_out = max((len(data['outgoing_signals']) for data in node_data.values()), default=0)
        max_targets_in = max((len(data['incoming_targets']) for data in node_data.values()), default=0)
        max_signals_in = max((len(data['incoming_signals']) for data in node_data.values()), default=0)

        # 出力CSVのヘッダーを作成
        header = ['from_id']  # ノードID
        header.extend([f'to_id_out{i}' for i in range(max_targets_out)])  # 出力先ノードID
        header.extend([f'to_id_in{i}' for i in range(max_targets_in)])    # 入力元ノードID
        header.append('height')  # ノードの高さ
        header.extend([f'sig_out{i}' for i in range(max_signals_out)])    # 出力信号
        header.extend([f'sig_in{i}' for i in range(max_signals_in)])      # 入力信号
        output_rows.append(header)

        # 各ノードのデータ行を作成
        for from_node, data in node_data.items():
            height = data['height']
            targets_out = data['outgoing_targets']
            signals_out = data['outgoing_signals']
            targets_in = data['incoming_targets']
            signals_in = data['incoming_signals']

            # 各リストを最大長に合わせてパディング（空文字で埋める）
            # これにより、すべての行が同じ列数を持つようになる
            # targets_outをmax_targets_outの長さに調整
            targets_out_padded = targets_out + [''] * (max_targets_out - len(targets_out))

            # targets_inをmax_targets_inの長さに調整
            targets_in_padded = targets_in + [''] * (max_targets_in - len(targets_in))

            # signals_outをmax_signals_outの長さに調整
            signals_out_padded = signals_out + [''] * (max_signals_out - len(signals_out))

            # signals_inをmax_signals_inの長さに調整
            signals_in_padded = signals_in + [''] * (max_signals_in - len(signals_in))
            
            # 出力行を作成し、行リストに追加
            output_row = [from_node] + targets_out_padded + targets_in_padded + [height] + signals_out_padded + signals_in_padded
            output_rows.append(output_row)

        # Draw.io用の設定部分を作成
        # これらの設定はDraw.ioがCSVをどのように解釈するかを指定する
        fp = open(output_csv_path, 'w')
        
        # ノードのラベルとして使用する列を指定
        setting_part_label = '# label: %from_id%\n'
        fp.write(setting_part_label)
        
        # ノードのスタイルを指定
        setting_part_style = '# style: label;\n'
        fp.write(setting_part_style)
        
        # レイアウトタイプを指定（水平フロー）
        setting_part_layout = '# layout: horizontalflow\n'
        fp.write(setting_part_layout)
        
        # ノードの高さを指定する列
        setting_part_height = '# height: @height\n'
        fp.write(setting_part_height)
        
        # 出力接続の設定
        for i in range(max_targets_out):
            # 各出力接続のスタイルと方向を指定
            setting_part_connect = f'# connect: {{"from":"to_id_out{i}", "to":"from_id", "fromlabel":"sig_out{i}", "invert": false, "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;curved=0;endArrow=blockThin;endFill=1;fontSize=11;"}}\n'
            fp.write(setting_part_connect)
        
        # 入力接続の設定
        for i in range(max_targets_in):
            # 各入力接続のスタイルと方向を指定（invertがtrueで方向が逆）
            setting_part_connect = f'# connect: {{"from":"to_id_in{i}", "to":"from_id", "fromlabel":"sig_in{i}", "invert": true, "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;curved=0;endArrow=blockThin;endFill=1;fontSize=11;"}}\n'
            fp.write(setting_part_connect)

        # 設定部分の書き込みを完了
        fp.close()

        # データ部分をCSVに追記
        with open(output_csv_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(output_rows)

        print(f"変換完了: '{output_csv_path}' に出力しました。")

    except FileNotFoundError:
        # 入力ファイルが見つからない場合のエラー処理
        print(f"エラー: 入力ファイル '{input_csv_path}' が見つかりません。")
    except Exception as e:
        # その他の例外処理
        print(f"エラーが発生しました: {e}")

# メイン処理
if __name__ == "__main__":
    # 入力ファイルと出力ファイルのパスを初期化
    input_file = ""
    output_file = ""
    
    # コマンドライン引数の数をチェック
    if len(sys.argv) == 3:
        # コマンドライン引数から入力・出力ファイルのパスを取得
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # GUIでファイル選択
        print("入力CSVファイルを選択してください...")
        input_file = select_file(title="入力CSVファイルを選択")
        
        # 入力ファイルが選択されなかった場合は終了
        if not input_file:
            print("入力ファイルが選択されませんでした。処理を終了します。")
            sys.exit(1)
            
        print("出力CSVファイルの保存先を選択してください...")
        output_file = select_save_file(title="出力CSVファイルの保存先を選択")
        
        # 出力ファイルが選択されなかった場合は終了
        if not output_file:
            print("出力ファイルが選択されませんでした。処理を終了します。")
            sys.exit(1)
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    
    # 変換処理を実行
    convert_csv_to_custom_format(input_file, output_file)
