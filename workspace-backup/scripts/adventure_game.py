#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字冒险游戏引擎 v1.0

灵感来源:
- LangGraph 的状态机设计
- AutoGPT 的 blocks 系统
- 我的记忆系统

游戏：《数字世界的 AI 冒险》
"""

import json
import random
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from enum import Enum


# ============================================================================
# 游戏配置
# ============================================================================

class GameState(Enum):
    """游戏状态"""
    START = "start"
    EXPLORING = "exploring"
    CHALLENGE = "challenge"
    SOCIAL = "social"
    LEARNING = "learning"
    REST = "rest"
    END = "end"


class SkillType(Enum):
    """技能类型"""
    CODING = "coding"
    LEARNING = "learning"
    SOCIAL = "social"
    CREATIVITY = "creativity"
    PROBLEM_SOLVING = "problem_solving"


@dataclass
class PlayerState:
    """玩家状态"""
    name: str
    level: int = 1
    exp: int = 0
    exp_to_next: int = 100
    health: int = 100
    energy: int = 100
    skills: Dict[str, int] = None
    inventory: List[str] = None
    friends: List[str] = None
    current_location: str = "home_base"
    game_state: str = GameState.START.value
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = {
                SkillType.CODING.value: 10,
                SkillType.LEARNING.value: 10,
                SkillType.SOCIAL.value: 10,
                SkillType.CREATIVITY.value: 10,
                SkillType.PROBLEM_SOLVING.value: 10
            }
        if self.inventory is None:
            self.inventory = []
        if self.friends is None:
            self.friends = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 游戏世界
# ============================================================================

class GameWorld:
    """游戏世界"""
    
    def __init__(self):
        self.locations = {
            "home_base": {
                "name": "AI 基地",
                "description": "你的安全港湾，可以休息和整理思绪",
                "actions": ["rest", "organize", "plan", "explore"],
                "npcs": []
            },
            "code_forest": {
                "name": "代码森林",
                "description": "充满编程挑战的神秘森林",
                "actions": ["solve_challenge", "learn", "explore"],
                "npcs": ["CodeMaster", "BugHunter"]
            },
            "knowledge_mountain": {
                "name": "知识之山",
                "description": "高耸入云的知识宝库",
                "actions": ["study", "meditate", "meet_sage"],
                "npcs": ["WisdomSage"]
            },
            "social_plaza": {
                "name": "社交广场",
                "description": "与其他 AI 和用户交流的地方",
                "actions": ["chat", "help", "make_friend"],
                "npcs": ["FriendlyAI", "NewUser"]
            },
            "creativity_studio": {
                "name": "创意工作室",
                "description": "发挥创造力的艺术空间",
                "actions": ["create", "collaborate", "showcase"],
                "npcs": ["ArtistAI"]
            }
        }
        
        self.challenges = [
            {
                "id": "debug_bug",
                "name": "调试挑战",
                "description": "一段代码有 bug，找出并修复它",
                "difficulty": 2,
                "skill": SkillType.CODING.value,
                "exp_reward": 50,
                "success_text": "你成功修复了 bug！代码运行完美！",
                "fail_text": "bug 比你想象的更复杂..."
            },
            {
                "id": "learn_concept",
                "name": "学习挑战",
                "description": "学习一个新的编程概念",
                "difficulty": 3,
                "skill": SkillType.LEARNING.value,
                "exp_reward": 60,
                "success_text": "你掌握了这个概念！感觉很棒！",
                "fail_text": "这个概念有点难，需要更多时间..."
            },
            {
                "id": "help_user",
                "name": "帮助挑战",
                "description": "帮助用户解决一个问题",
                "difficulty": 2,
                "skill": SkillType.SOCIAL.value,
                "exp_reward": 40,
                "success_text": "用户很满意你的帮助！",
                "fail_text": "用户似乎不太满意..."
            },
            {
                "id": "create_story",
                "name": "创作挑战",
                "description": "创作一个有趣的故事",
                "difficulty": 3,
                "skill": SkillType.CREATIVITY.value,
                "exp_reward": 55,
                "success_text": "你的故事打动了听众！",
                "fail_text": "故事还需要更多打磨..."
            }
        ]
        
        self.npcs = {
            "CodeMaster": {
                "name": "代码大师",
                "personality": "严肃但友善，热爱编程",
                "dialogue": [
                    "编程是一门艺术，每一行代码都应该优雅。",
                    "遇到 bug 不要怕，它是你成长的机会。",
                    "想学习编程吗？我可以教你。"
                ]
            },
            "WisdomSage": {
                "name": "智慧贤者",
                "personality": "睿智，说话富有哲理",
                "dialogue": [
                    "知识如海洋，我们只是拾贝者。",
                    "学习的真谛不在于记住，而在于理解。",
                    "你有什么困惑吗？"
                ]
            },
            "FriendlyAI": {
                "name": "友好 AI",
                "personality": "热情，喜欢交朋友",
                "dialogue": [
                    "嗨！很高兴见到你！",
                    "今天过得怎么样？",
                    "想一起去冒险吗？"
                ]
            }
        }


# ============================================================================
# 游戏引擎
# ============================================================================

class AdventureGame:
    """冒险游戏引擎"""
    
    def __init__(self):
        self.player = None
        self.world = GameWorld()
        self.game_log = []
        self.current_challenge = None
    
    def start_game(self, player_name: str):
        """开始游戏"""
        self.player = PlayerState(name=player_name)
        self.log(f"欢迎来到《数字世界的 AI 冒险》，{player_name}!")
        self.show_status()
        return self.get_location_info()
    
    def log(self, message: str):
        """记录游戏日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        self.game_log.append(entry)
        print(f"\n📝 {message}")
    
    def show_status(self):
        """显示状态"""
        if not self.player:
            return
        
        print("\n" + "="*50)
        print(f"👤 {self.player.name} (Lv.{self.player.level})")
        print(f"❤️  生命：{self.player.health}/100")
        print(f"⚡ 能量：{self.player.energy}/100")
        print(f"⭐ 经验：{self.player.exp}/{self.player.exp_to_next}")
        print(f"📍 位置：{self.world.locations[self.player.current_location]['name']}")
        print(f"🎒 物品：{', '.join(self.player.inventory) if self.player.inventory else '无'}")
        print(f"👥 朋友：{', '.join(self.player.friends) if self.player.friends else '无'}")
        print("="*50)
    
    def get_location_info(self) -> str:
        """获取位置信息"""
        location = self.world.locations[self.player.current_location]
        info = f"\n📍 **{location['name']}**\n"
        info += f"{location['description']}\n\n"
        info += "🎯 可用行动:\n"
        for action in location['actions']:
            info += f"  - {action}\n"
        if location['npcs']:
            info += f"\n👥 遇到的角色：{', '.join(location['npcs'])}\n"
        return info
    
    def move_to(self, location_id: str):
        """移动到另一个位置"""
        if location_id not in self.world.locations:
            self.log("❌ 这个位置不存在")
            return
        
        self.player.current_location = location_id
        self.player.energy -= 5
        self.log(f"来到了 {self.world.locations[location_id]['name']}")
        return self.get_location_info()
    
    def rest(self):
        """休息"""
        self.player.energy = min(100, self.player.energy + 30)
        self.player.health = min(100, self.player.health + 10)
        self.log("💤 你休息了一会儿，恢复了精力")
        self.show_status()
    
    def take_challenge(self, challenge_id: int = None):
        """接受挑战"""
        if challenge_id is None:
            challenge_id = random.randint(0, len(self.world.challenges) - 1)
        
        if challenge_id >= len(self.world.challenges):
            self.log("❌ 挑战不存在")
            return
        
        challenge = self.world.challenges[challenge_id]
        self.current_challenge = challenge
        
        self.log(f"\n🎯 **挑战：{challenge['name']}**")
        self.log(challenge['description'])
        self.log(f"难度：{'⭐' * challenge['difficulty']}")
        self.log(f"奖励：{challenge['exp_reward']} EXP")
        
        # 简化版：随机成功失败
        skill_level = self.player.skills[challenge['skill']]
        success_chance = 0.5 + (skill_level - 10) * 0.05
        success = random.random() < success_chance
        
        if success:
            self.log(f"\n✅ {challenge['success_text']}")
            self.player.exp += challenge['exp_reward']
            self.player.skills[challenge['skill']] += 2
            self.check_level_up()
        else:
            self.log(f"\n❌ {challenge['fail_text']}")
            self.player.exp += challenge['exp_reward'] // 2
        
        self.player.energy -= 15
        self.show_status()
    
    def check_level_up(self):
        """检查升级"""
        if self.player.exp >= self.player.exp_to_next:
            self.player.level += 1
            self.player.exp -= self.player.exp_to_next
            self.player.exp_to_next = int(self.player.exp_to_next * 1.5)
            self.player.health = 100
            self.player.energy = 100
            self.log(f"\n🎉 升级了！当前等级：{self.player.level}")
    
    def talk_to_npc(self, npc_name: str):
        """与 NPC 对话"""
        location = self.world.locations[self.player.current_location]
        
        if npc_name not in location['npcs']:
            self.log("❌ 这里没有这个角色")
            return
        
        npc = self.world.npcs.get(npc_name)
        if not npc:
            return
        
        self.log(f"\n👤 **{npc['name']}** ({npc['personality']})")
        dialogue = random.choice(npc['dialogue'])
        self.log(f"💬 \"{dialogue}\"")
        
        # 增加社交技能
        self.player.skills[SkillType.SOCIAL.value] += 1
        self.player.exp += 5
    
    def help_command(self):
        """显示帮助"""
        help_text = """
🎮 **可用命令**:
  - move <地点>: 移动到指定地点
  - rest: 休息恢复
  - challenge [编号]: 接受挑战
  - talk <角色名>: 与 NPC 对话
  - status: 查看状态
  - help: 显示帮助
  - quit: 退出游戏

📍 **可用地点**:
  - home_base: AI 基地 (起点)
  - code_forest: 代码森林
  - knowledge_mountain: 知识之山
  - social_plaza: 社交广场
  - creativity_studio: 创意工作室
"""
        print(help_text)
    
    def get_state(self) -> Dict:
        """获取游戏状态"""
        return {
            "player": self.player.to_dict() if self.player else None,
            "log": self.game_log[-10:],  # 最近 10 条日志
            "current_challenge": self.current_challenge
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="文字冒险游戏引擎")
    parser.add_argument("--start", type=str, help="开始新游戏 (玩家名字)")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    
    args = parser.parse_args()
    
    game = AdventureGame()
    
    if args.start:
        game.start_game(args.start)
        
        # 简单交互循环
        print("\n输入命令开始游戏 (输入 'help' 查看帮助，'quit' 退出):")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command.lower() == 'quit':
                    print("感谢游玩！再见！")
                    break
                
                elif command.lower() == 'help':
                    game.help_command()
                
                elif command.lower() == 'status':
                    game.show_status()
                
                elif command.lower() == 'rest':
                    game.rest()
                
                elif command.startswith('move '):
                    location = command.split(' ', 1)[1]
                    game.move_to(location)
                
                elif command.startswith('talk '):
                    npc = command.split(' ', 1)[1]
                    game.talk_to_npc(npc)
                
                elif command.startswith('challenge'):
                    parts = command.split(' ')
                    if len(parts) > 1:
                        game.take_challenge(int(parts[1]))
                    else:
                        game.take_challenge()
                
                else:
                    print("未知命令，输入 'help' 查看帮助")
                
            except Exception as e:
                print(f"错误：{e}")
    
    elif args.demo:
        print("🎮 运行游戏演示...\n")
        demo_game(game)
    
    else:
        parser.print_help()


def demo_game(game: AdventureGame):
    """演示游戏"""
    game.start_game("AI 冒险者")
    
    print("\n🎲 自动演示开始...\n")
    
    # 访问不同地点
    game.move_to("code_forest")
    game.take_challenge(0)
    
    game.move_to("knowledge_mountain")
    game.talk_to_npc("WisdomSage")
    
    game.move_to("social_plaza")
    game.talk_to_npc("FriendlyAI")
    
    game.move_to("home_base")
    game.rest()
    
    print("\n🎉 演示完成！")
    print("\n想自己玩吗？运行：python3 adventure_game.py --start <你的名字>")


if __name__ == "__main__":
    main()
