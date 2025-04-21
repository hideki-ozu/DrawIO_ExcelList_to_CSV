import csv
from collections import defaultdict
import sys

def convert_csv_to_custom_format(input_csv_path, output_csv_path):
    node_data = defaultdict(lambda: {
        'outgoing_targets': [],
        'outgoing_signals': [],
        'incoming_targets': [],
        'incoming_signals': [],
        'incoming_count': 0,
        'outgoing_count': 0,
        'height': 0
    })

    try:
        with open(input_csv_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            if not reader.fieldnames or not all(f in reader.fieldnames for f in ['From', 'Signal', 'Dist', 'To']):
                 print(f"エラー: 入力CSV '{input_csv_path}' に必要なヘッダー（'From', 'Signal', 'Dist', 'To'）がありません。")
                 return

            for row in reader:
                from_node = row.get('From')
                signal = row.get('Signal')
                dist = row.get('Dist')
                to_node = row.get('To')

                if not all([from_node, signal, dist, to_node]):
                    print(f"警告: 不完全なデータ行をスキップしました: {row}")
                    continue

                from_node = from_node.strip()
                to_node = to_node.strip()
                signal = signal.strip()

                source = from_node
                target = to_node

                if dist.upper() == 'OUT':
                    node_data[source]['outgoing_targets'].append(target)
                    node_data[source]['outgoing_signals'].append(signal)
                    node_data[source]['outgoing_count'] += 1
                    node_data[target]['incoming_count'] += 1
                elif dist.upper() == 'IN':
                    node_data[source]['incoming_targets'].append(target)
                    node_data[source]['incoming_signals'].append(signal)
                    node_data[source]['incoming_count'] += 1
                    node_data[target]['outgoing_count'] += 1
                else:
                    print(f"警告: 不明なDist値 '{dist}' を含む行をスキップしました: {row}")
                    continue

        for node in node_data:
            in_count = node_data[node]['incoming_count']
            out_count = node_data[node]['outgoing_count']
            node_data[node]['height'] = max(in_count, out_count) * 14

        output_rows = []
        max_targets_out = max((len(data['outgoing_targets']) for data in node_data.values()), default=0)
        max_signals_out = max((len(data['outgoing_signals']) for data in node_data.values()), default=0)
        max_targets_in = max((len(data['incoming_targets']) for data in node_data.values()), default=0)
        max_signals_in = max((len(data['incoming_signals']) for data in node_data.values()), default=0)

        header = ['from_id']
        header.extend([f'to_id_out{i}' for i in range(max_targets_out)])
        header.extend([f'to_id_in{i}' for i in range(max_targets_in)])
        header.append('height')
        header.extend([f'sig_out{i}' for i in range(max_signals_out)])
        header.extend([f'sig_in{i}' for i in range(max_signals_in)])
        output_rows.append(header)

        for from_node, data in node_data.items():
            height = data['height']
            targets_out = data['outgoing_targets']
            signals_out = data['outgoing_signals']
            targets_in = data['incoming_targets']
            signals_in = data['incoming_signals']

            # targets_outをmax_targets_outの長さに調整
            targets_out_padded = targets_out + [''] * (max_targets_out - len(targets_out))

            # targets_inをmax_targets_inの長さに調整
            targets_in_padded = targets_in + [''] * (max_targets_in - len(targets_in))

            # signals_outをmax_signals_outの長さに調整
            signals_out_padded = signals_out + [''] * (max_signals_out - len(signals_out))

            # signals_inをmax_signals_inの長さに調整
            signals_in_padded = signals_in + [''] * (max_signals_in - len(signals_in))
            output_row = [from_node] + targets_out_padded + targets_in_padded + [height] + signals_out_padded + signals_in_padded
            output_rows.append(output_row)

        # 設定部作成
        fp = open(output_csv_path, 'w')
        setting_part_label = '# label: %from_id%\n'
        fp.write(setting_part_label)
        setting_part_style = '# style: label;\n'
        fp.write(setting_part_style)
        setting_part_layout = '# layout: horizontalflow\n'
        fp.write(setting_part_layout)
        setting_part_height = '# height: @height\n'
        fp.write(setting_part_height)
        
        for i in range(max_targets_out):
            setting_part_connect = f'# connect: {{"from":"to_id_out{i}", "to":"from_id", "fromlabel":"sig_out{i}", "invert": false, "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;curved=0;endArrow=blockThin;endFill=1;fontSize=11;"}}\n'
            fp.write(setting_part_connect)
        for i in range(max_targets_in):
            setting_part_connect = f'# connect: {{"from":"to_id_in{i}", "to":"from_id", "fromlabel":"sig_in{i}", "invert": true, "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;curved=0;endArrow=blockThin;endFill=1;fontSize=11;"}}\n'
            fp.write(setting_part_connect)

        fp.close()

        with open(output_csv_path, 'a', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(output_rows)

        print(f"変換完了: '{output_csv_path}' に出力しました。")

    except FileNotFoundError:
        print(f"エラー: 入力ファイル '{input_csv_path}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用法: python converter.py <入力CSVファイルパス> <出力CSVファイルパス>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_csv_to_custom_format(input_file, output_file)

