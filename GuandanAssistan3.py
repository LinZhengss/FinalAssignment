import sys
import random
from collections import defaultdict
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QFileDialog, QLineEdit, QVBoxLayout, QWidget, 
                            QListWidget, QHBoxLayout, QTextEdit, 
                            QGroupBox, QGridLayout, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime

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
        self._last_suggestion = []  # 缓存上次建议
    
    def reset_game(self):
        """重置游戏状态"""
        self.hand_cards = []         # 当前手牌
        self.played_cards = []       # 已出牌列表
        self.opponent_history = []   # 对手出牌历史
        self.round_count = 0         # 当前轮次
        self.current_turn = "me"     # 当前出牌方: me/opponent
        self.current_round_cards = [] # 当前轮对手出的牌
        self.opponent_card_type = None  # 对手出牌类型
        self._last_suggestion = []   # 清空缓存
    
    def update_hand(self, cards):
        """更新当前手牌"""
        self.hand_cards = sorted(cards, key=self.card_value)
        self._last_suggestion = []  # 手牌更新后重置缓存
    
    def record_opponent_play(self, cards):
        """记录对手出牌"""
        if cards:
            # 识别对手出牌类型
            self.opponent_card_type = self._identify_card_type(cards)
            self.opponent_history.append((self.round_count, cards, self.opponent_card_type))
            self.current_round_cards = cards
            self.current_turn = "me"  # 对手出牌后轮到我们
            self._last_suggestion = []  # 对手出牌后重置缓存
    
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
            self.opponent_card_type = None   # 重置对手牌型
            self._last_suggestion = []  # 我方出牌后重置缓存
    
    def reset_round(self):
        """重置当前轮次状态"""
        self.current_round_cards = []
        self.opponent_card_type = None
        self.current_turn = "opponent" if self.current_turn == "me" else "me"
        self._last_suggestion = []  # 重置缓存
    
    def suggest_play(self, force_recalculate=False):
        """生成出牌建议"""
        # 如果强制重新计算或缓存为空，则重新计算
        if force_recalculate or not self._last_suggestion:
            self._last_suggestion = self._calculate_suggestion()
        return self._last_suggestion
    
    def _calculate_suggestion(self):
        """实际计算建议的核心方法"""
        # 根据游戏状态选择策略
        if not self.current_round_cards and self.current_turn == "me":
            return self._lead_play()  # 先手出牌
        elif self.current_round_cards and self.current_turn == "me":
            return self._counter_play()  # 应对出牌
        else:
            return []  # 对手回合不给出建议
    
    def _lead_play(self):
        """先手出牌策略"""
        # 策略1: 优先出小牌
        if len(self.hand_cards) > 5:
            return self.hand_cards[:1]  # 出最小单张
        
        # 策略2: 找对子
        pairs = self._find_pairs()
        if pairs:
            # 选择最小的对子
            return min(pairs, key=lambda p: max(self.card_value(card) for card in p))
        
        # 策略3: 出顺子
        sequences = self._find_sequences()
        if sequences:
            # 选择最小的顺子
            return min(sequences, key=lambda s: max(self.card_value(card) for card in s))
        
        # 默认出最小牌
        return self.hand_cards[:1]
    
    def _counter_play(self):
        """应对出牌策略：考虑牌型匹配"""
        if not self.current_round_cards or not self.opponent_card_type:
            return self._lead_play()
        
        # 根据对手牌型寻找匹配的牌型
        if self.opponent_card_type["type"] == "single":
            return self._counter_single()
        elif self.opponent_card_type["type"] == "pair":
            return self._counter_pair()
        elif self.opponent_card_type["type"] == "sequence":
            return self._counter_sequence()
        elif self.opponent_card_type["type"] == "bomb":
            return self._counter_bomb()
        else:
            return []
    
    def _counter_single(self):
        """应对单张牌"""
        opponent_value = self.card_value(self.current_round_cards[0])
        # 找能压制的最小单张
        playable_cards = [card for card in self.hand_cards 
                         if self.card_value(card) > opponent_value]
        
        if playable_cards:
            return [min(playable_cards, key=self.card_value)]
        return []
    
    def _counter_pair(self):
        """应对对子"""
        # 对手对子的值
        opponent_value = self.card_value(self.current_round_cards[0])
        
        # 找出所有对子
        pairs = self._find_pairs()
        
        # 找出能压制对手的对子
        playable_pairs = []
        for pair in pairs:
            if self.card_value(pair[0]) > opponent_value:
                playable_pairs.append(pair)
        
        if playable_pairs:
            # 选择最小压制对子
            return min(playable_pairs, key=lambda p: max(self.card_value(card) for card in p))
        
        # 没有对子，找炸弹
        bombs = self._find_bombs()
        if bombs:
            return bombs[0]
        
        return []
    
    def _counter_sequence(self):
        """应对顺子 - 修复版"""
        # 对手顺子的长度和最大值
        seq_length = len(self.current_round_cards)
        opponent_max = max(self.card_value(card) for card in self.current_round_cards)
        
        # 找出所有顺子
        sequences = self._find_sequences()
        
        # 找出能压制对手的顺子（相同长度且最大值更大）
        playable_sequences = []
        for seq in sequences:
            if len(seq) == seq_length:
                seq_max = max(self.card_value(card) for card in seq)
                if seq_max > opponent_max:
                    playable_sequences.append(seq)
        
        # 关键修复：如果没有相同长度的顺子，找更长的顺子
        if not playable_sequences:
            for seq in sequences:
                if len(seq) > seq_length:  # 允许用更长的顺子压制
                    playable_sequences.append(seq)
        
        if playable_sequences:
            # 选择最小压制顺子（最小最大牌值）
            return min(playable_sequences, key=lambda s: max(self.card_value(card) for card in s))
        
        # 没有顺子，找炸弹
        bombs = self._find_bombs()
        if bombs:
            return bombs[0]
        
        return []
    
    def _counter_bomb(self):
        """应对炸弹"""
        # 对手炸弹的值
        bomb_value = self.card_value(self.current_round_cards[0])
        
        # 找出所有炸弹
        bombs = self._find_bombs()
        
        # 找出能压制对手的炸弹
        playable_bombs = []
        for bomb in bombs:
            if self.card_value(bomb[0]) > bomb_value:
                playable_bombs.append(bomb)
        
        if playable_bombs:
            # 选择最小压制炸弹
            return min(playable_bombs, key=lambda b: max(self.card_value(card) for card in b))
        
        # 没有炸弹，找更大的炸弹（如四张以上）
        big_bombs = [bomb for bomb in bombs if len(bomb) > 4]
        if big_bombs:
            return big_bombs[0]
        
        return []
    
    def _identify_card_type(self, cards):
        """识别牌型"""
        if not cards:
            return {"type": "pass", "size": 0}
            
        card_values = sorted([self.card_value(card) for card in cards])
        
        # 单张
        if len(cards) == 1:
            return {"type": "single", "value": card_values[0]}
        
        # 对子
        if len(cards) == 2 and card_values[0] == card_values[1]:
            return {"type": "pair", "value": card_values[0]}
        
        # 顺子（5张或以上）
        if len(cards) >= 5:
            # 检查是否连续
            is_sequence = True
            for i in range(1, len(card_values)):
                if card_values[i] - card_values[i-1] != 1:
                    is_sequence = False
                    break
            
            if is_sequence:
                return {"type": "sequence", "length": len(cards), "max": max(card_values)}
        
        # 炸弹（4张或以上相同值）
        if len(cards) >= 4:
            if all(v == card_values[0] for v in card_values):
                return {"type": "bomb", "value": card_values[0], "size": len(cards)}
        
        # 其他牌型（如三带二等）暂不处理
        return {"type": "other", "size": len(cards)}
    
    def _find_pairs(self):
        """找出所有对子"""
        value_count = defaultdict(list)
        for card in self.hand_cards:
            value = self.card_value(card)
            value_count[value].append(card)
        
        # 返回所有对子（至少2张相同值）
        return [cards[:2] for cards in value_count.values() if len(cards) >= 2]
    
    def _find_sequences(self):
        """找出所有顺子（5张或以上）- 修复版"""
        if len(self.hand_cards) < 5:
            return []
        
        # 按牌值排序
        sorted_cards = sorted(self.hand_cards, key=self.card_value)
        card_values = [self.card_value(card) for card in sorted_cards]
        unique_values = sorted(set(card_values))
        
        sequences = []
        
        # 找出所有可能的顺子
        for start in range(len(unique_values)):
            for end in range(start + 5, len(unique_values) + 1):
                # 检查是否连续
                is_sequence = True
                for i in range(start + 1, end):
                    if unique_values[i] - unique_values[i-1] != 1:
                        is_sequence = False
                        break
                
                if is_sequence:
                    # 提取连续牌
                    seq_values = unique_values[start:end]
                    seq_cards = []
                    for val in seq_values:
                        # 为每个值找一张牌
                        for card in sorted_cards:
                            if self.card_value(card) == val and card not in seq_cards:
                                seq_cards.append(card)
                                break
                    sequences.append(seq_cards)
        
        return sequences
    
    def _find_bombs(self):
        """找出炸弹（4张或以上相同值）"""
        value_count = defaultdict(list)
        for card in self.hand_cards:
            value = self.card_value(card)
            value_count[value].append(card)
        
        bombs = []
        for value, cards in value_count.items():
            if len(cards) >= 4:  # 四张或以上相同值
                bombs.append(cards)
        
        return bombs
    
    @staticmethod
    def card_value(card):
        """计算牌面数值 - 修复版"""
        # 提取牌值部分
        value_str = card[2:]
        
        # 特殊牌值映射
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
            state += f"对手出牌: {' '.join(self.current_round_cards)}\n"
            if self.opponent_card_type:
                state += f"对手牌型: {self._format_card_type(self.opponent_card_type)}\n"
        
        return state
    
    def _format_card_type(self, card_type):
        """格式化牌型信息"""
        if card_type["type"] == "single":
            return f"单张({card_type['value']})"
        elif card_type["type"] == "pair":
            return f"对子({card_type['value']})"
        elif card_type["type"] == "sequence":
            return f"{card_type['length']}张顺子(最大{card_type['max']})"
        elif card_type["type"] == "bomb":
            return f"{card_type['size']}张炸弹({card_type['value']})"
        elif card_type["type"] == "pass":
            return "不出"
        else:
            return f"其他牌型({card_type['size']}张)"

# 增强的用户界面
class GuandanAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("掼蛋辅助机器人 - 专业版")
        self.setGeometry(100, 100, 900, 700)
        
        # 初始化AI和识别器
        self.ai = GuandanAI()
        self.recognizer = CardRecognizer()
        self.last_suggestion_time = None
        
        # 创建主窗口和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板 - 手牌管理
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # 游戏控制区
        control_group = QGroupBox("游戏控制")
        control_layout = QVBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        self.reset_btn = QPushButton("🆕 新游戏")
        self.reset_btn.clicked.connect(self.reset_game)
        self.reset_btn.setStyleSheet("font-size: 14px; font-weight: bold; height: 40px; background-color: #4CAF50; color: white;")
        control_layout.addWidget(self.reset_btn)
        
        self.camera_btn = QPushButton("📷 扫描手牌")
        self.camera_btn.clicked.connect(self.capture_cards)
        self.camera_btn.setStyleSheet("font-size: 14px; height: 40px; background-color: #2196F3; color: white;")
        control_layout.addWidget(self.camera_btn)
        
        left_panel.addWidget(control_group)
        
        # 手牌显示区
        hand_group = QGroupBox("🃏 我的手牌")
        hand_layout = QVBoxLayout(hand_group)
        hand_layout.setSpacing(10)
        
        self.hand_list = QListWidget()
        self.hand_list.setSelectionMode(QListWidget.MultiSelection)
        self.hand_list.setStyleSheet("font-size: 14px; min-height: 200px;")
        hand_layout.addWidget(self.hand_list)
        
        # 操作按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        self.play_btn = QPushButton("🃏 出牌")
        self.play_btn.clicked.connect(self.play_selected_cards)
        self.play_btn.setStyleSheet("font-size: 14px; height: 35px; background-color: #FF9800; color: white;")
        button_layout.addWidget(self.play_btn)
        
        self.pass_btn = QPushButton("⏭️ 跳过")
        self.pass_btn.clicked.connect(self.pass_turn)
        self.pass_btn.setStyleSheet("font-size: 14px; height: 35px; background-color: #9E9E9E; color: white;")
        button_layout.addWidget(self.pass_btn)
        
        self.identify_btn = QPushButton("🔍 识别牌型")
        self.identify_btn.clicked.connect(self.identify_selected_cards)
        self.identify_btn.setStyleSheet("font-size: 14px; height: 35px; background-color: #9C27B0; color: white;")
        button_layout.addWidget(self.identify_btn)
        
        hand_layout.addLayout(button_layout)
        
        left_panel.addWidget(hand_group)
        
        # 对手出牌区
        opponent_group = QGroupBox("👤 对手出牌")
        opponent_layout = QVBoxLayout(opponent_group)
        opponent_layout.setSpacing(10)
        
        self.opponent_input = QLineEdit()
        self.opponent_input.setPlaceholderText("输入对手出牌，空格分隔 (例: 红桃5 方块5)")
        self.opponent_input.setStyleSheet("font-size: 14px; padding: 8px;")
        opponent_layout.addWidget(self.opponent_input)
        
        self.record_opponent_btn = QPushButton("📝 记录对手出牌")
        self.record_opponent_btn.clicked.connect(self.record_opponent_play)
        self.record_opponent_btn.setStyleSheet("font-size: 14px; height: 35px; background-color: #F44336; color: white;")
        opponent_layout.addWidget(self.record_opponent_btn)
        
        # 添加对手出牌类型显示
        self.opponent_type_label = QLabel("对手牌型: 未记录")
        self.opponent_type_label.setStyleSheet("font-size: 14px; color: #D32F2F; font-weight: bold; padding: 5px;")
        opponent_layout.addWidget(self.opponent_type_label)
        
        left_panel.addWidget(opponent_group)
        
        # 右侧面板 - 游戏状态和建议
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # 游戏状态区
        status_group = QGroupBox("📊 游戏状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setStyleSheet("font-size: 14px; background-color: #E3F2FD; min-height: 150px;")
        status_layout.addWidget(self.status_display)
        
        right_panel.addWidget(status_group)
        
        # AI建议区
        suggestion_group = QGroupBox("🤖 出牌建议")
        suggestion_layout = QVBoxLayout(suggestion_group)
        suggestion_layout.setSpacing(10)
        
        # 建议信息头
        suggestion_header = QHBoxLayout()
        self.suggestion_label = QLabel("建议出牌: ")
        self.suggestion_label.setStyleSheet("font-size: 16px; color: #1976D2; font-weight: bold;")
        suggestion_header.addWidget(self.suggestion_label)
        
        self.suggestion_time_label = QLabel("")
        self.suggestion_time_label.setStyleSheet("font-size: 12px; color: #757575;")
        suggestion_header.addStretch()
        suggestion_header.addWidget(self.suggestion_time_label)
        
        suggestion_layout.addLayout(suggestion_header)
        
        self.suggestion_list = QListWidget()
        self.suggestion_list.setStyleSheet("font-size: 14px; background-color: #E8F5E9; min-height: 120px;")
        suggestion_layout.addWidget(self.suggestion_list)
        
        # 建议操作按钮
        suggestion_buttons = QHBoxLayout()
        suggestion_buttons.setSpacing(5)
        
        self.play_suggestion_btn = QPushButton("✅ 采用建议")
        self.play_suggestion_btn.clicked.connect(self.play_suggested_cards)
        self.play_suggestion_btn.setStyleSheet("font-size: 14px; height: 35px; background-color: #4CAF50; color: white;")
        suggestion_buttons.addWidget(self.play_suggestion_btn)
        
        self.refresh_suggestion_btn = QPushButton("🔄 更新建议")
        self.refresh_suggestion_btn.clicked.connect(self.update_suggestion)
        self.refresh_suggestion_btn.setStyleSheet("font-size: 14px; height: 35px; background-color: #FFC107; color: black;")
        suggestion_buttons.addWidget(self.refresh_suggestion_btn)
        
        suggestion_layout.addLayout(suggestion_buttons)
        
        # 建议类型显示
        self.suggestion_type_label = QLabel("建议牌型: 无")
        self.suggestion_type_label.setStyleSheet("font-size: 14px; color: #2E7D32; font-weight: bold; padding: 5px;")
        suggestion_layout.addWidget(self.suggestion_type_label)
        
        # 添加顺子长度提示
        self.sequence_hint = QLabel("💡 提示: 顺子长度可大于对手顺子 | 炸弹可压制任何牌型")
        self.sequence_hint.setStyleSheet("font-size: 13px; color: #388E3C; padding: 5px;")
        suggestion_layout.addWidget(self.sequence_hint)
        
        right_panel.addWidget(suggestion_group)
        
        # 出牌历史区
        history_group = QGroupBox("📜 出牌历史")
        history_layout = QVBoxLayout(history_group)
        
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setStyleSheet("font-size: 14px; background-color: #FFF8E1; min-height: 150px;")
        history_layout.addWidget(self.history_display)
        
        right_panel.addWidget(history_group)
        
        # 组合布局
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 3)
        
        # 添加状态栏
        self.statusBar().showMessage("就绪 | 欢迎使用掼蛋辅助机器人")
        
        # 设置初始大小
        self.setMinimumSize(900, 650)
    
    def reset_game(self):
        """重置游戏"""
        self.ai.reset_game()
        self.hand_list.clear()
        self.opponent_input.clear()
        self.suggestion_list.clear()
        self.history_display.clear()
        self.opponent_type_label.setText("对手牌型: 未记录")
        self.suggestion_time_label.setText("")
        self.suggestion_type_label.setText("建议牌型: 无")
        self.update_game_display()
        self.update_suggestion()
        self.statusBar().showMessage("新游戏已开始，请扫描手牌")
        QMessageBox.information(self, "新游戏", "已开始新游戏，请扫描手牌")
    
    def capture_cards(self):
        """模拟拍照识别过程"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择手牌照片", "", "图片文件 (*.png *.jpg)"
        )
        
        if file_name:
            # 识别卡片
            cards = self.recognizer.recognize_cards(file_name)
            self.hand_list.clear()
            self.hand_list.addItems(cards)
            self.ai.update_hand(cards)
            self.update_game_display()
            self.update_suggestion()
            self.statusBar().showMessage(f"已扫描手牌: {len(cards)}张", 3000)
    
    def record_opponent_play(self):
        """记录对手出牌"""
        opponent_cards = self.opponent_input.text().split()
        if not opponent_cards:
            QMessageBox.warning(self, "输入错误", "请输入对手出牌")
            return
        
        # 验证出牌是否合法
        for card in opponent_cards:
            if len(card) < 3:
                QMessageBox.warning(self, "输入错误", f"无效的牌: {card}")
                return
        
        self.ai.record_opponent_play(opponent_cards)
        self.opponent_input.clear()
        self.update_game_display()
        self.update_suggestion()
        
        # 更新对手牌型显示
        if self.ai.opponent_card_type:
            self.opponent_type_label.setText(
                f"对手牌型: {self.ai._format_card_type(self.ai.opponent_card_type)}"
            )
        
        # 添加到历史记录
        self.history_display.append(
            f"第{self.ai.round_count+1}轮 - 对手出牌: {' '.join(opponent_cards)} "
            f"({self.ai._format_card_type(self.ai.opponent_card_type)})"
        )
        self.statusBar().showMessage(f"已记录对手出牌: {len(opponent_cards)}张", 3000)
    
    def play_selected_cards(self):
        """出选中的牌"""
        selected_items = self.hand_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "出牌错误", "请选择要出的牌")
            return
        
        cards = [item.text() for item in selected_items]
        self.ai.record_my_play(cards)
        
        # 从手牌列表移除
        for item in selected_items:
            self.hand_list.takeItem(self.hand_list.row(item))
        
        # 关键修复：重置当前轮次状态
        self.ai.reset_round()
        
        # 添加到历史记录
        card_type = self.ai._identify_card_type(cards)
        self.history_display.append(
            f"第{self.ai.round_count}轮 - 我方出牌: {' '.join(cards)} "
            f"({self.ai._format_card_type(card_type)})"
        )
        
        self.update_game_display()
        self.update_suggestion()
        self.statusBar().showMessage(f"已出牌: {len(cards)}张", 3000)
    
    def identify_selected_cards(self):
        """识别选中牌的牌型"""
        selected_items = self.hand_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "操作错误", "请选择要识别的牌")
            return
        
        cards = [item.text() for item in selected_items]
        card_type = self.ai._identify_card_type(cards)
        
        QMessageBox.information(
            self, 
            "牌型识别", 
            f"您选择的牌: {' '.join(cards)}\n"
            f"牌型: {self.ai._format_card_type(card_type)}"
        )
        self.statusBar().showMessage(f"已识别牌型: {self.ai._format_card_type(card_type)}", 3000)
    
    def pass_turn(self):
        """跳过当前回合"""
        self.ai.record_my_play([])
        self.ai.reset_round()
        
        # 添加到历史记录
        self.history_display.append(f"第{self.ai.round_count}轮 - 我方跳过")
        
        self.update_game_display()
        self.update_suggestion()
        self.statusBar().showMessage("已跳过当前回合", 3000)
        QMessageBox.information(self, "跳过回合", "您选择了跳过当前回合")
    
    def play_suggested_cards(self):
        """采用AI建议出牌"""
        if self.suggestion_list.count() == 0:
            QMessageBox.warning(self, "出牌错误", "没有可用的出牌建议")
            return
        
        # 获取建议的牌
        suggested_cards = []
        for i in range(self.suggestion_list.count()):
            suggested_cards.append(self.suggestion_list.item(i).text())
        
        # 从手牌列表中选中建议的牌
        self.hand_list.clearSelection()
        for i in range(self.hand_list.count()):
            item = self.hand_list.item(i)
            if item.text() in suggested_cards:
                item.setSelected(True)
        
        # 自动出牌
        self.play_selected_cards()
    
    def update_suggestion(self):
        """更新出牌建议 - 增强版"""
        # 记录更新时间
        update_time = datetime.now().strftime("%H:%M:%S")
        self.suggestion_time_label.setText(f"更新时间: {update_time}")
        
        # 检查是否有手牌
        if not self.ai.hand_cards:
            self.suggestion_list.clear()
            self.suggestion_label.setText("建议出牌: 请先扫描手牌")
            self.suggestion_type_label.setText("建议牌型: 无")
            self.statusBar().showMessage("无法更新建议: 无手牌数据", 3000)
            return
        
        # 添加视觉反馈动画
        self.refresh_suggestion_btn.setText("🔄 计算中...")
        QApplication.processEvents()  # 立即更新UI
        
        # 强制重新计算建议
        suggestion = self.ai.suggest_play(force_recalculate=True)
        self.suggestion_list.clear()
        
        # 0.3秒后恢复按钮文本
        QTimer.singleShot(300, lambda: self.refresh_suggestion_btn.setText("🔄 更新建议"))
        
        if suggestion:
            self.suggestion_list.addItems(suggestion)
            self.suggestion_label.setText(f"建议出牌 ({len(suggestion)}张):")
            
            # 识别并显示建议牌型
            card_type = self.ai._identify_card_type(suggestion)
            self.suggestion_type_label.setText(
                f"建议牌型: {self.ai._format_card_type(card_type)}"
            )
            
            # 状态栏反馈
            self.statusBar().showMessage(f"建议已更新 | {update_time}", 3000)
            
            # 添加历史记录
            self.history_display.append(
                f"[{update_time}] 建议更新: {' '.join(suggestion)} " +
                f"({self.ai._format_card_type(card_type)})"
            )
        else:
            self.suggestion_label.setText("建议: 不出")
            self.suggestion_type_label.setText("建议牌型: 无")
            
            # 根据游戏状态给出原因
            reason = "未知原因"
            if not self.ai.current_round_cards and self.ai.current_turn == "me":
                reason = "先手出牌，但未找到合适牌型"
            elif self.ai.current_round_cards and self.ai.current_turn == "me":
                reason = "无法压制对手出牌"
            elif self.ai.current_turn == "opponent":
                reason = "当前是对手回合"
            
            # 状态栏反馈
            self.statusBar().showMessage(f"建议: 不出 | 原因: {reason}", 3000)
            
            # 添加历史记录
            self.history_display.append(
                f"[{update_time}] 建议更新: 不出 ({reason})"
            )
    
    def update_game_display(self):
        """更新游戏状态显示"""
        state = self.ai.get_game_state()
        self.status_display.setText(state)
        
        # 更新手牌列表
        if self.hand_list.count() == 0 and self.ai.hand_cards:
            self.hand_list.addItems(self.ai.hand_cards)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = GuandanAssistant()
    window.show()
    sys.exit(app.exec_())