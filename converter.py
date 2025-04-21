import csv

# 2. 入力ファイルからデータを読み込む関数
def read_source_data(input_path):
    """
    指定されたパスのCSVファイルからデータを読み込みます。

    Args:
        input_path (str): 入力CSVファイルのパス。

    Returns:
        list: ヘッダーを除いたCSVデータのリスト。各行は辞書形式。
              例: [{'From': 'node_0', 'Signal': 'sig00_0_to_1', 'Dist': 'OUT', 'To': 'node_1'}, ...]
              エラー発生時は空のリストを返す。
    """
    data = []
    try:
        with open(input_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"エラー: 入力ファイルが見つかりません: {input_path}")
    except Exception as e:
        print(f"エラー: 入力ファイルの読み込み中にエラーが発生しました: {e}")
    return data

# 3. 読み込んだデータを加工する関数
def process_data(source_data):
    """
    読み込んだデータをdraw.io用のCSV形式に加工します。

    Args:
        source_data (list): read_source_data関数で読み込んだデータのリスト。

    Returns:
        list: draw.ioインポート用のCSVデータリスト。
              各行はリスト形式: [edge_label, source_node, target_node]
              例: [['sig00_0_to_1', 'node_0', 'node_1'], ...]
    """
    drawio_data = []
    # draw.io CSVのヘッダーを追加
    drawio_data.append(['# label', 'source', 'target'])
    # データ行を追加
    for row in source_data:
        from_node = row.get('From')
        signal = row.get('Signal')
        dist = row.get('Dist')
        to_node = row.get('To')

        if not all([from_node, signal, dist, to_node]):
            print(f"警告: 不完全なデータ行をスキップしました: {row}")
            continue

        if dist.upper() == 'OUT':
            source = from_node
            target = to_node
        elif dist.upper() == 'IN':
            source = to_node
            target = from_node
        else:
            print(f"警告: 不明なDist値 '{dist}' を含む行をスキップしました: {row}")
            continue

        drawio_data.append([signal, source, target])

    return drawio_data

# 4. 加工したデータを出力する関数
def write_drawio_csv(output_path, drawio_data):
    """
    加工したデータを指定されたパスにCSVファイルとして出力します。

    Args:
        output_path (str): 出力CSVファイルのパス。
        drawio_data (list): process_data関数で加工されたdraw.io用データのリスト。

    Returns:
        bool: 出力が成功した場合はTrue、失敗した場合はFalse。
    """
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(drawio_data)
        return True
    except Exception as e:
        print(f"エラー: 出力ファイルの書き込み中にエラーが発生しました: {e}")
        return False

# 1. main部
def main():
    """
    プログラムのエントリーポイント。
    入力ファイルの読み込み、データ加工、出力ファイルへの書き込みを実行します。
    """
    input_file = 'source_data.csv'
    output_file = 'drawio_input.csv'

    print(f"入力ファイル: {input_file}")
    source_data = read_source_data(input_file)

    if not source_data:
        print("入力データが空のため、処理を終了します。")
        return

    print(f"{len(source_data)} 件のデータを読み込みました。")

    print("データをdraw.io形式に加工しています...")
    drawio_data = process_data(source_data)

    print(f"加工後のデータ件数（ヘッダー含む）: {len(drawio_data)}")

    print(f"出力ファイル: {output_file}")
    if write_drawio_csv(output_file, drawio_data):
        print("draw.io用CSVファイルの作成が完了しました。")
    else:
        print("draw.io用CSVファイルの作成に失敗しました。")

if __name__ == "__main__":
    main()
