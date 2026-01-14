import itertools
from collections import defaultdict
import time
import sys

class GameTheorySolver:
    def __init__(self):
        print("正在初始化全量空间 (0000-9999)...")
        # 全集：用于作为“探测器”
        self.all_combinations = [''.join(p) for p in itertools.product('0123456789', repeat=4)]
        # 候选集：可能是答案的集合
        self.candidates = self.all_combinations.copy()
        self.turn = 0

    def calculate_score(self, target, guess):
        """位置和数值都对才算对"""
        return sum(1 for t, g in zip(target, guess) if t == g)

    def get_best_guess(self):
        self.turn += 1
        
        # === 阶段 1: 开局定式 (为了秒回) ===
        # 0123 是信息熵最高的开局
        if self.turn == 1:
            return "0123"

        # 如果只剩 1-2 个，直接猜，不用算博弈了
        if len(self.candidates) <= 2:
            return self.candidates[0]

        print(f"   [分析] 剩余 {len(self.candidates)} 个嫌疑项。正在寻找最佳探测数...")

        # === 阶段 2: 性能分层策略 ===
        
        # 策略 A: 如果剩余项太多 (>500)，全局搜索太慢。
        # 使用“强力覆盖”策略，强制探测未涉及的数字区间。
        if len(self.candidates) > 500:
            if self.turn == 2: return "4567"
            if self.turn == 3: return "8901"
            # 如果还没筛完，就从候选池里选一个最能切割的
            search_space = self.candidates
        else:
            # 策略 B: 终极博弈 (Global Minimax)
            # 当候选数 < 500 时，我们遍历 0000-9999 所有数字，
            # 寻找那个能把剩余候选数切分得最细的数字（哪怕它本身不可能是答案）
            search_space = self.all_combinations

        best_guess = self.candidates[0]
        min_worst_case = float('inf')
        
        # 进度显示优化
        total_search = len(search_space)
        check_step = max(1, total_search // 10) # 每10%显示一次

        for i, guess in enumerate(search_space):
            # 简单的进度条
            if len(search_space) > 2000 and i % check_step == 0:
                sys.stdout.write(f"\r   >> 正在推演: {int(i/total_search*100)}%")
                sys.stdout.flush()

            score_counts = defaultdict(int)
            
            # 模拟：如果我猜 guess，真实答案是 candidates 里的某一个，会发生什么？
            for cand in self.candidates:
                score = self.calculate_score(cand, guess)
                score_counts[score] += 1
            
            # Minimax 核心：找出最坏情况（剩余数量最大）
            worst_case = max(score_counts.values())

            # 只有当这个猜测的最坏情况比当前记录的更好时，才更新
            if worst_case < min_worst_case:
                min_worst_case = worst_case
                best_guess = guess
            
            # 如果最坏情况一样，优先选择“可能是答案”的数字 (Consistent Guess)
            # 这样万一运气好能直接赢
            elif worst_case == min_worst_case:
                if guess in self.candidates:
                    best_guess = guess

            # 剪枝：如果最坏情况是1，说明这个猜测能完美区分所有剩余项，直接用
            if min_worst_case == 1:
                break
        
        if len(search_space) > 2000:
            print("") # 换行

        return best_guess

    def update(self, guess, real_score):
        before = len(self.candidates)
        self.candidates = [c for c in self.candidates if self.calculate_score(c, guess) == real_score]
        after = len(self.candidates)
        print(f"   -> 排除 {before - after} 项，剩余 {after} 项")
        
        if after == 0:
            print("!!! 异常：剩余可能性为0，请检查刚才的反馈输入是否正确 !!!")
            return False
        return True

def main():
    print("========================================")
    print("      猜数字 (Global Minimax)    ")
    print("========================================")
    print("特点：")
    print("1. 可能会建议你猜一个【绝对错误】的数字。")
    print("2. 目的不是为了这一把猜中，而是为了下一把必中。")
    print("========================================\n")
    
    solver = GameTheorySolver()
    step = 0
    while True:
        t0 = time.time()
        guess = solver.get_best_guess()
        t1 = time.time()
        step += 1
        print(f"### step {step} ###\n>>> 建议猜测：【 {guess} 】 (计算耗时 {t1-t0:.2f}s)")
        
        while True:
            s = input("设定者反馈几对? (0-4): ")
            if s.isdigit() and 0 <= int(s) <= 4:
                score = int(s)
                break
        
        if score == 4:
            print(f"恭喜！答案是 {guess} 适用{step}轮破解成功！")
            break
            
        if not solver.update(guess, score):
            break

    input("程序执行完毕，按回车键退出...") 

if __name__ == "__main__":
    main()
