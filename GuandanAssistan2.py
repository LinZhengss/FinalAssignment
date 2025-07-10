import sys
import random
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QFileDialog, QLineEdit, QVBoxLayout, QWidget, 
                            QListWidget, QHBoxLayout, QTextEdit, QComboBox,
                            QGroupBox, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt

# 扑克牌识别器（模拟版）
class CardRecognizer:
    def recognize_cards(self, image_path):
        """模拟图像识别过程"""
        suits = ["红桃", "方块", "梅花", "黑桃"]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        # 确保不重复
        cards = set()
        while len(cards) < 13:  # 掼蛋每人13张牌
            card = f"{random.choice(suits)}{random.choice(values)}"
            cards.add(card)
        return list(cards)

# 增强的掼蛋AI引擎
class GuandanAI:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        self.hand_cards = []         # 当前手牌
        self.played_cards = []       # 已出牌列表
        self.opponent_history = []   # 对手出牌历史
        self.round_count = 0         # 当前轮次
        self.current_turn = "me"     # 当前出牌方: me/opponent
        self.current_round_cards = [] # 当前轮对手出的牌
    
    def update_hand(self, cards):
        """更新当前手牌"""
        self.hand_cards = sorted(cards, key=self.card_value)
    
    def record_opponent_play(self, cards):
        """记录对手出牌"""
        if cards:
            self.opponent_history.append((self.round_count, cards))
            self.current_round_cards = cards
            self.current_turn = "me"  # 对手出牌后轮到我们
    
    def record_my_play(self, cards):
        """记录我方出牌"""
        if cards:
            self.played_cards.extend(cards)
            # 从手牌中移除
            for card in cards:
                if card in self.hand_cards:
                    self.hand_cards.remove(card)
            self.round_count += 1
            self.current_turn = "opponent"  # 我方出牌后轮到对手
            self.current_round_cards = []   # 重置当前轮
    
    def suggest_play(self):
        """生成出牌建议"""
        if not self.current_round_cards and self.current_turn == "me":
            return self._lead_play()  # 先手出牌
        elif self.current_round_cards and self.current_turn == "me":
            return self._counter_play()  # 应对出牌
        else:
            return []  # 对手回合不给出建议
    
    def _lead_play(self):
        """先手出牌策略：优先出最小对子"""
        pairs = self._find_valid_pairs()
        if pairs:
            # 返回最小的有效对子
            return list(min(pairs, key=lambda p: self.card_value(p[0])))
        
        # 没有对子则考虑其他牌型
        sequences = self._find_sequences()
        if sequences:
            return random.choice(sequences)
        
        # 最后出单张
        return self.hand_cards[:1]
    
    def _counter_play(self):
        """应对出牌策略"""
        opponent_type = self._identify_card_type(self.current_round_cards)
        
        if opponent_type == "single":
            return self._counter_single()
        elif opponent_type == "pair":
            return self._counter_pair()
        elif opponent_type == "sequence":
            return self._counter_sequence()
        elif opponent_type == "bomb":
            return self._counter_bomb()
        else:
            return []
    
    def _counter_single(self):
        """应对单牌"""
        opponent_value = self.card_value(self.current_round_cards[0])
        playable_cards = [card for card in self.hand_cards 
                         if self.card_value(card) > opponent_value]
        
        if playable_cards:
            return [min(playable_cards, key=self.card_value)]
        return []
    
    def _counter_pair(self):
        """精确对子压制逻辑"""
        if not self._is_valid_pair(self.current_round_cards):
            return []
        
        opponent_value = self.card_value(self.current_round_cards[0])
        my_pairs = self._find_valid_pairs()
        
        # 找出所有能压制对手的对子
        valid_pairs = [pair for pair in my_pairs 
                      if self.card_value(pair[0]) > opponent_value]
        
        if valid_pairs:
            # 返回能压制的最小对子
            return list(min(valid_pairs, key=lambda p: self.card_value(p[0])))
        return []
    
    def _counter_sequence(self):
        """应对顺子"""
        if not self._is_valid_sequence(self.current_round_cards):
            return []
        
        opponent_values = [self.card_value(card) for card in self.current_round_cards]
        opponent_min = min(opponent_values)
        
        # 找出所有可能的顺子
        my_sequences = self._find_sequences()
        
        # 找出能压制对手的顺子(最小牌大于对手顺子的最小牌)
        valid_sequences = [seq for seq in my_sequences 
                          if min(self.card_value(card) for card in seq) > opponent_min]
        
        if valid_sequences:
            # 返回能压制的最小顺子(按最小牌排序)
            return min(valid_sequences, key=lambda s: min(self.card_value(card) for card in s))
        return []
    
    def _find_valid_pairs(self):
        """找出所有有效对子（确保花色不同）"""
        value_count = defaultdict(list)
        for card in sorted(self.hand_cards, key=self.card_value):
            value = card[2:]  # 提取牌值部分
            value_count[value].append(card)
        
        # 返回排序后的对子元组列表
        return [tuple(sorted(pair[:2], key=self.card_value)) 
               for pair in value_count.values() if len(pair) >= 2]
    
    def _is_valid_pair(self, cards):
        """验证是否为有效对子"""
        return (len(cards) == 2 and 
                cards[0][2:] == cards[1][2:] and  # 数值相同
                cards[0][:2] != cards[1][:2])     # 花色不同
    
    def _is_valid_sequence(self, cards):
        """验证是否为有效顺子(5张连续牌)"""
        if len(cards) != 5:
            return False
        
        # 提取牌值并去重
        values = sorted(set(self.card_value(card) for card in cards))
        if len(values) != 5:  # 有重复牌值
            return False
        
        # 检查是否连续
        return values[-1] - values[0] == 4
    
    def _identify_card_type(self, cards):
        """识别牌型"""
        if len(cards) == 1:
            return "single"
        elif self._is_valid_pair(cards):
            return "pair"
        elif len(cards) == 4 and len(set(c[2:] for c in cards)) == 1:
            return "bomb"
        elif self._is_valid_sequence(cards):
            return "sequence"
        else:
            return "unknown"
    
    def _find_sequences(self):
        """找出所有顺子"""
        if len(self.hand_cards) < 5:
            return []
        
        values = sorted(set(self.card_value(card) for card in self.hand_cards))
        sequences = []
        
        for i in range(len(values) - 4):
            if values[i+4] - values[i] == 4:
                sequence = []
                for val in range(values[i], values[i]+5):
                    for card in self.hand_cards:
                        if self.card_value(card) == val and card not in sequence:
                            sequence.append(card)
                            break
                if len(sequence) == 5:
                    sequences.append(sequence)
        
        return sequences
    
    def _find_bombs(self):
        """找出炸弹"""
        value_count = defaultdict(list)
        for card in self.hand_cards:
            value = card[2:]  # 提取牌值部分
            value_count[value].append(card)
        
        bombs = []
        for cards in value_count.values():
            if len(cards) >= 4:  # 四张或以上相同值
                bombs.append(cards[:4])
        
        return bombs
    
    @staticmethod
    def card_value(card):
        """计算牌面数值"""
        value_str = card[2:]
        
        value_map = {
            "2": 15, "A": 14, "K": 13, "Q": 12, "J": 11,
            "10": 10, "9": 9, "8": 8, "7": 7, "6": 6,
            "5": 5, "4": 4, "3": 3
        }
        return value_map.get(value_str, 0)
    
    def get_game_state(self):
        """获取当前游戏状态摘要"""
        state = f"当前轮次: {self.round_count + 1}\n"
        state += f"当前出牌方: {'我方' if self.current_turn == 'me' else '对手'}\n"
        state += f"剩余手牌: {len(self.hand_cards)}张\n"
        state += f"已出牌: {len(self.played_cards)}张\n"
        
        if self.current_round_cards:
            card_type = self._identify_card_type(self.current_round_cards)
            state += f"当前轮对手出牌({card_type}): {' '.join(self.current_round_cards)}\n"
        
        return state

# 用户界面
class GuandanAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("掼蛋辅助机器人 - 专业版")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化AI和识别器
        self.ai = GuandanAI()
        self.recognizer = CardRecognizer()
        
        # 创建主窗口和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 手牌管理
        left_panel = QVBoxLayout()
        
        # 游戏控制区
        control_group = QGroupBox("游戏控制")
        control_layout = QVBoxLayout(control_group)
        
        self.reset_btn = QPushButton("新游戏")
        self.reset_btn.clicked.connect(self.reset_game)
        control_layout.addWidget(self.reset_btn)
        
        self.camera_btn = QPushButton("扫描手牌")
        self.camera_btn.clicked.connect(self.capture_cards)
        control_layout.addWidget(self.camera_btn)
        
        left_panel.addWidget(control_group)
        
        # 手牌显示区
        hand_group = QGroupBox("我的手牌")
        hand_layout = QVBoxLayout(hand_group)
        
        self.hand_list = QListWidget()
        self.hand_list.setSelectionMode(QListWidget.MultiSelection)
        hand_layout.addWidget(self.hand_list)
        
        self.play_btn = QPushButton("出牌")
        self.play_btn.clicked.connect(self.play_selected_cards)
        hand_layout.addWidget(self.play_btn)
        
        left_panel.addWidget(hand_group)
        
        # 对手出牌区
        opponent_group = QGroupBox("对手出牌")
        opponent_layout = QVBoxLayout(opponent_group)
        
        self.opponent_input = QLineEdit()
        self.opponent_input.setPlaceholderText("输入对手出牌，空格分隔（如：红桃5 方块5）")
        opponent_layout.addWidget(self.opponent_input)
        
        self.record_opponent_btn = QPushButton("记录对手出牌")
        self.record_opponent_btn.clicked.connect(self.record_opponent_play)
        opponent_layout.addWidget(self.record_opponent_btn)
        
        left_panel.addWidget(opponent_group)
        
        # 右侧面板 - 游戏状态和建议
        right_panel = QVBoxLayout()
        
        # 游戏状态区
        status_group = QGroupBox("游戏状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        status_layout.addWidget(self.status_display)
        
        right_panel.addWidget(status_group)
        
        # AI建议区
        suggestion_group = QGroupBox("出牌建议")
        suggestion_layout = QVBoxLayout(suggestion_group)
        
        self.suggestion_label = QLabel("建议出牌: ")
        self.suggestion_label.setStyleSheet("font-size: 16px; color: blue;")
        suggestion_layout.addWidget(self.suggestion_label)
        
        self.suggestion_list = QListWidget()
        suggestion_layout.addWidget(self.suggestion_list)
        
        self.play_suggestion_btn = QPushButton("采用建议")
        self.play_suggestion_btn.clicked.connect(self.play_suggested_cards)
        suggestion_layout.addWidget(self.play_suggestion_btn)
        
        right_panel.addWidget(suggestion_group)
        
        # 出牌历史区
        history_group = QGroupBox("出牌历史")
        history_layout = QVBoxLayout(history_group)
        
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        history_layout.addWidget(self.history_display)
        
        right_panel.addWidget(history_group)
        
        # 组合布局
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 3)
        
        # 初始状态
        self.update_game_display()
    
    def reset_game(self):
        """重置游戏"""
        self.ai.reset_game()
        self.hand_list.clear()
        self.opponent_input.clear()
        self.suggestion_list.clear()
        self.history_display.clear()
        self.update_game_display()
        QMessageBox.information(self, "新游戏", "已开始新游戏，请扫描手牌")
    
    def capture_cards(self):
        """模拟拍照识别过程"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择手牌照片", "", "图片文件 (*.png *.jpg)"
        )
        
        if file_name:
            cards = self.recognizer.recognize_cards(file_name)
            self.hand_list.clear()
            self.hand_list.addItems(cards)
            self.ai.update_hand(cards)
            self.update_game_display()
            self.update_suggestion()
    
    def record_opponent_play(self):
        """记录对手出牌"""
        opponent_cards = self.opponent_input.text().split()
        if not opponent_cards:
            QMessageBox.warning(self, "输入错误", "请输入对手出牌")
            return
        
        for card in opponent_cards:
            if len(card) < 3:
                QMessageBox.warning(self, "输入错误", f"无效的牌: {card}")
                return
        
        self.ai.record_opponent_play(opponent_cards)
        self.opponent_input.clear()
        self.update_game_display()
        self.update_suggestion()
        
        card_type = self.ai._identify_card_type(opponent_cards)
        self.history_display.append(f"第{self.ai.round_count+1}轮 - 对手出牌({card_type}): {' '.join(opponent_cards)}")
    
    def play_selected_cards(self):
        """出选中的牌"""
        selected_items = self.hand_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "出牌错误", "请选择要出的牌")
            return
        
        cards = [item.text() for item in selected_items]
        self.ai.record_my_play(cards)
        
        for item in selected_items:
            self.hand_list.takeItem(self.hand_list.row(item))
        
        card_type = self.ai._identify_card_type(cards)
        self.history_display.append(f"第{self.ai.round_count}轮 - 我方出牌({card_type}): {' '.join(cards)}")
        
        self.update_game_display()
        self.update_suggestion()
    
    def play_suggested_cards(self):
        """采用AI建议出牌"""
        if self.suggestion_list.count() == 0:
            QMessageBox.warning(self, "出牌错误", "没有可用的出牌建议")
            return
        
        suggested_cards = []
        for i in range(self.suggestion_list.count()):
            suggested_cards.append(self.suggestion_list.item(i).text())
        
        self.hand_list.clearSelection()
        for i in range(self.hand_list.count()):
            item = self.hand_list.item(i)
            if item.text() in suggested_cards:
                item.setSelected(True)
        
        self.play_selected_cards()
    
    def update_suggestion(self):
        """更新出牌建议"""
        suggestion = self.ai.suggest_play()
        self.suggestion_list.clear()
        
        if suggestion:
            card_type = self.ai._identify_card_type(suggestion)
            self.suggestion_label.setText(f"建议出牌({card_type}):")
            self.suggestion_list.addItems(suggestion)
        else:
            self.suggestion_label.setText("建议: 不出")
    
    def update_game_display(self):
        """更新游戏状态显示"""
        state = self.ai.get_game_state()
        self.status_display.setText(state)
        
        if self.hand_list.count() == 0 and self.ai.hand_cards:
            self.hand_list.addItems(self.ai.hand_cards)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GuandanAssistant()
    window.show()
    sys.exit(app.exec_())