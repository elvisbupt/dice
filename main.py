import random
import operator
import numpy as np

VALUE_WIN = {
    '2': 3,  # 2名玩家, 当吹牛除自己以外的目标数字数量为3及以上,输掉的概率会超过五成。
    '3': 4,
    '4': 6,
    '5': 8,
}




FALG_CONTINUE = 10000
MAX_ROLL = 6

def bprint(discrib, value):
    s = '==============================='+ str(discrib)+'=='+str(value)
    print(s)
    with open("log.txt", "a") as f:
        f.write(s+'\n')  # 自带文件关闭功能，不需要再写f.close()

class Game():  # 一局游戏的类
    def __init__(self, playerN, diceN):
        self.playerNum = playerN  # 一局几个玩家
        self.diceNum = diceN  # 一局几个骰子
        self.roundCur = 0  # 当前第几局
        self.curStatus = 0  # 一局的状态 0起始，
        self.curPlayerID = 0  # 当前游戏到了第几个玩家
        self.lastLoser = 0  # 上一次谁输了，从他开始

        self.lastNum = 0 #上个人叫的数量
        self.lastRoll = 0 #上个人叫的点数
        self.diceValue = [] # 所有玩家点数数组
        self.arrayRoll = [0]*6 # 汇总每个玩家的总点数

        self.lostRoll = 100
        for key in VALUE_WIN:
            if int(key) == self.playerNum:
                self.lostRoll = VALUE_WIN[key]  # 获取当前玩家数量的前提下，除自己以外，上家叫几个骰子会输
                #bprint(VALUE_WIN, self.lostRoll)
                break

    def init_game(self, lLoser):  # 本局游戏初始化
        self.curStatus = 0  # 一局的状态 0当前玩家叫数，1有玩家开，判断输赢，结束游戏
        self.curPlayer = 0  # 当前游戏到了第几个玩家
        self.lastLoser = lLoser  # 从上一个输家开始游戏

    def next_round(self):  # 本剧游戏到下一个回合 curRoll本次叫的点数
        self.curPlayerID = (self.curPlayerID + 1) % self.playerNum

    def return_curPlayer(self):
        return self.curPlayer

    def return_curStatus(self):
        return self.curStatus

    def return_lastLoser(self):
        return self.lastLoser

    def build_last_call(self, lNum, lRoll):
        self.lastNum = lNum
        self.lastRoll = lRoll

    def return_last_call(self):
        return (self.lastNum, self.lastRoll)

    def return_lostRoll(self):
        return self.lostRoll

    def gather_roll(self, aRoll): # 获取每个玩家的点数
        self.diceValue = self.diceValue+ aRoll

    def count_roll(self): # 将原始点数数组统计为m个n 11224变为[2, 4, 2, 3, 2, 2]
        num_one = 0  # 1点有几个
        for i in range(len(self.diceValue)): # 统计1点个数
            if self.diceValue[i] == 1:
                num_one += 1
        i = 0

        bprint('totol======diceValue', self.diceValue)
        for i in range(len(self.diceValue)):
            self.arrayRoll[self.diceValue[i] - 1] += 1  # 例子 如果当前点数为1，则array_roll[1-1] += 1
        if num_one > 0:
            for i in range(1, len(self.arrayRoll)):
                self.arrayRoll[i] += num_one  # 1点算任意值，其他点个数需要加上1点个数
        bprint('totol======arrayRoll', self.arrayRoll)

    def settle(self, cNum, cRoll): # 有玩家开，结算游戏
        #bprint('curID1', self.curPlayerID)
        #bprint('cNum', cNum)
        #bprint('cRoll', cRoll)
        if self.lastNum == 0: # 第一次叫
            self.lastNum = cNum
            self.lastRoll = cRoll
            self.next_round()
            return FALG_CONTINUE
        else: # 不是第一次叫，要判断游戏是否结束
            if not cNum == 0: # 当前用户没开，继续
                self.lastNum = cNum
                self.lastRoll = cRoll
                self.next_round()
                return FALG_CONTINUE
            else: # cNum==0,当前用户开了
                #bprint('arrayRoll', self.arrayRoll)
                #bprint('self.lastRoll', self.lastRoll)
                #bprint('self.lastNum', self.lastNum)
                if self.arrayRoll[self.lastRoll-1] >= self.lastNum:
                    loserID = self.curPlayerID
                else:
                    loserID = (self.curPlayerID-1+self.playerNum)%self.playerNum

                return loserID


class Player():  # 玩家类
    def __init__(self, id, tac, nDice, fPerson, lostRoll):  # tactics策略
        self.tactics = tac  # 机器策略，0是保守，1是激进
        self.numDice = nDice  # 一局几个骰子
        self.flagPerson = fPerson  # 是否是人类，0是机器，1是人类
        self.arrayRoll = [0] * 6  # 记录每个点数有几个的数组，数组第一个数字记录1点有几个，以此类推
        self.ID = id
        self.diceValue = []
        self.arrayWeight = [0]*6 #统计每个点数的权重，每个player不一样
        self.ret = 0.5 # 激进概率
        # 加入cheat权重
        maxCheat = list(range(int(lostRoll / 3) + 1))
        self.aCheat = []
        for i in range(MAX_ROLL):
            self.aCheat.append(random.choice(maxCheat))

    def return_aWeight(self): # 得到本局权重数组（哪个点分别被叫了几次）
        return self.arrayWeight

    def update_weight(self, cRoll):
        self.arrayWeight[curRoll - 1] += 1

    def return_ID(self):
        return self.ID

    def init_dice(self):  # 初始化骰子值

        for i in range(self.numDice):
            value = int(random.randint(1, 6))
            self.diceValue.append(value)
        num_one = 0 #  1点有几个
        for i in range(len(self.diceValue)):
            if self.diceValue[i] == 1:
                num_one += 1

        bprint('开始扔骰子，玩家ID是', self.ID)
        self.diceValue.sort() # 原始点数数组可以排序
        bprint('原始骰子数组是diceValue', self.diceValue)
        for i in range(len(self.diceValue)):
            self.arrayRoll[self.diceValue[i]-1] += 1  # 例子 如果当前点数为1，则array_roll[1-1] += 1

        if num_one > 0:
            for i in range(1, len(self.arrayRoll)):
                self.arrayRoll[i] += num_one # 1点算任意值，其他点个数需要加上1点个数
        #bprint('整理点数个数的数组arrayRoll', self.arrayRoll )


    # 保守策略，开始叫
    def decide_conser_start(self, playerNum):
        max_index, max_number = max(enumerate(self.arrayRoll), key=operator.itemgetter(1))
        num = max_number+1 if max_number+1 >= playerNum else playerNum # 最少叫玩家个数的骰子
        bprint('###########保守##第一个叫，当前玩家ID是', self.ID)
        bprint('#########选择的个数是', num)
        bprint('#########选择的点数是', max_index + 1)
        return num, max_index+1

    # 激进策略，开始叫
    def decide_radical_start(self, playerNum):
        t_ret = random.random()
        bprint('###########激进为主t_ret', t_ret)
        if t_ret < self.ret:
            return self.decide_conser_start(playerNum)
        else: # 执行激进策略,诈一下，叫随机点数
            lRoll = random.randint(1,6)
            lNum = playerNum
            bprint('###########激进##第一个叫，当前玩家ID是', self.ID)
            bprint('#########选择的个数是', lNum)
            bprint('#########选择的点数是', lRoll)
            return lNum, lRoll

    # 激进策略，不是第一个叫 aWeight权重数组 lostR根据如果根据VALUE_WIN得到的大概率输的值
    def decide_radical_ing(self, num, roll, lostR):
        t_ret = random.random()
        if t_ret < self.ret:
            return self.decide_conser_ing(num, roll, lostR)
        else:  # 执行激进策略,诈一下，叫随机点数
            bprint('###########激进策略', 1)
            if num - self.arrayRoll[roll - 1] >= lostR:  # 如果根据VALUE_WIN，上家冒了直接开
                bprint('###########当前玩家ID是', self.ID)
                bprint('###########玩家选择开上家 lostR=', lostR)
                return (0, 0)
            else:
                # 如果上家叫了1，本局只能叫1
                if roll == 1:
                    bprint('###########根据数量最多叫，当前玩家ID是', self.ID)
                    bprint('#########选择的个数是', num + 1)
                    bprint('#########选择的点数是', 1)
                    return num + 1, 1

                # 生成所有可以叫的组合，存在二维数组中
                arrayPossi = []
                for i in range(1, 7):
                    # n = num+1 if i==roll else num
                    if i > roll:  # 如果点数比已叫的大，数量和已叫相同
                        n = num
                    else:  # 如果点数没有已叫大，则数量需要+1
                        n = num + 1
                    arrayPossi.append(n)

                # bprint('arrayPossi', arrayPossi)
                # 计算每个组合的安全值-叫数
                i = 0
                a_temp = []  # 叫数-实际数量
                for i in range(6):
                    a_temp.append(arrayPossi[i] - self.arrayRoll[i] - self.aCheat[i])
                bprint('诈骗权重aCheat', self.aCheat)
                bprint('数量计算结果a_temp', a_temp)

                # 找出最小值 a_result为所有最小值的索引id
                a_result = np.argwhere(a_temp == np.amin(a_temp))
                a_result = a_result.flatten().tolist()
                # bprint('a_result1', a_result)
                # 返回最小值的组合（如果存在不止一个最小值，选权重最大的）
                if len(a_result) == 1:
                    bprint('###########根据数量最多叫，当前玩家ID是', self.ID)
                    bprint('#########选择的个数是', arrayPossi[a_result[0]])
                    bprint('#########选择的点数是', a_result[0] + 1)
                    return (arrayPossi[a_result[0]], a_result[0] + 1)
                else:  # 不止一个最小值
                    a_addWeight = []
                    i = 0
                    for i in range(6):
                        a_addWeight.append(arrayPossi[i] - self.arrayRoll[i] - self.arrayWeight[i]- self.aCheat[i])
                    a_result = np.argwhere(a_addWeight == np.amin(a_addWeight))
                    a_result = a_result.flatten().tolist()
                    bprint('权重计算后结果a_addWeight', a_addWeight)
                    if len(a_result) == 1:
                        bprint('###########经过最大权重计算叫，当前玩家ID是', self.ID)
                        bprint('#########选择的个数是', arrayPossi[a_result[0]])
                        bprint('#########选择的点数是', a_result[0] + 1)
                        return (arrayPossi[a_result[0]], a_result[0] + 1)
                    else:  # 加上权重也不止一个最小值，随机选个最小值
                        t_roll = random.choice(a_result)
                        t_num = arrayPossi[t_roll]
                        bprint('###########经过随机权重计算叫，当前玩家ID是', self.ID)
                        bprint('#########选择的个数是', t_num)
                        bprint('#########选择的点数是', t_roll + 1)
                        return (t_num, t_roll + 1)

    # 保守策略，不是第一个叫 aWeight权重数组 lostR根据如果根据VALUE_WIN得到的大概率输的值
    def decide_conser_ing(self, num, roll, lostR):
        bprint('###########保守策略', 1)
        if num - self.arrayRoll[roll - 1] >= lostR: # 如果根据VALUE_WIN，上家冒了直接开
            bprint('###########当前玩家ID是', self.ID)
            bprint('###########玩家选择开上家 lostR=', lostR)
            return (0, 0)
        else:
            #如果上家叫了1，本局只能叫1
            if roll == 1:
                bprint('###########根据数量最多叫，当前玩家ID是', self.ID)
                bprint('#########选择的个数是', num+1)
                bprint('#########选择的点数是', 1)
                return num+1, 1
            # 生成所有可以叫的组合，存在二维数组中
            arrayPossi = []
            for i in range(1, 7):
                #n = num+1 if i==roll else num
                if i > roll: # 如果点数比已叫的大，数量和已叫相同
                    n = num
                else: # 如果点数没有已叫大，则数量需要+1
                    n = num+1
                arrayPossi.append(n)

            #bprint('arrayPossi', arrayPossi)
            # 计算每个组合的安全值-叫数
            i = 0
            a_temp = [] #叫数-实际数量
            for i in range(6):
                a_temp.append(arrayPossi[i] - self.arrayRoll[i])
            bprint('数量计算结果a_temp', a_temp)

            # 找出最小值 a_result为所有最小值的索引id
            a_result = np.argwhere(a_temp == np.amin(a_temp))
            a_result = a_result.flatten().tolist()
            #bprint('a_result1', a_result)
            # 返回最小值的组合（如果存在不止一个最小值，选权重最大的）
            if len(a_result) == 1:
                bprint('###########根据数量最多叫，当前玩家ID是', self.ID)
                bprint('#########选择的个数是', arrayPossi[a_result[0]])
                bprint('#########选择的点数是', a_result[0]+1)
                return (arrayPossi[a_result[0]], a_result[0]+1)
            else: # 不止一个最小值
                a_addWeight = []
                i = 0
                for i in range(6):
                    a_addWeight.append(arrayPossi[i] - self.arrayRoll[i]-self.arrayWeight[i])
                a_result = np.argwhere(a_addWeight == np.amin(a_addWeight))
                a_result = a_result.flatten().tolist()
                bprint('权重计算后结果a_addWeight', a_addWeight)
                if  len(a_result) == 1:
                    bprint('###########经过最大权重计算叫，当前玩家ID是', self.ID)
                    bprint('#########选择的个数是', arrayPossi[a_result[0]])
                    bprint('#########选择的点数是', a_result[0]+1)
                    return (arrayPossi[a_result[0]], a_result[0]+1)
                else: #加上权重也不止一个最小值，随机选个最小值
                    t_roll = random.choice(a_result)
                    t_num = arrayPossi[t_roll]
                    bprint('###########经过随机权重计算叫，当前玩家ID是', self.ID)
                    bprint('#########选择的个数是', t_num)
                    bprint('#########选择的点数是', t_roll+1)
                    return (t_num, t_roll+1)

    def decide(self, lnum, lroll, lostR, playerNum):  # 做决策 num=0表示从自己第一个开始叫点数
        if self.flagPerson == 1: # 如果是人类
            flag = 1
            bprint('self.diceValue', self.diceValue)
            while(flag):
                tNum = int(input('请输入要叫的骰子数量，0表示开上家:'))
                if not (isinstance(tNum, int) and tNum >= 0):
                    print('必须输入正整数')
                    continue
                if lnum == 0 and tNum < playerNum:  # 叫的点数数量为0，表示从自己开始第一个叫
                    print('第一次叫，骰子数量不能小于玩家数')
                    continue
                else: # 判断是否直接开
                    if tNum == 0:
                        bprint('###########经过人脑计算，当前玩家ID是', self.ID)
                        bprint('#########选择开上家',11)
                        return 0, 0

                tRoll = int(input('请输入要叫的骰子点数:'))
                if not (isinstance(tRoll, int) and tRoll >= 1 and tRoll <= 6):
                    print('必须输入1到6的整数')
                    continue
                if lroll==1 and not tRoll==1 :
                    print('上家叫1，接下来必须叫1')
                    continue
                if not ((tNum > lnum and tRoll <= lroll) or (tNum >= lnum and tRoll > lroll)):
                    print('数量和点数至少有1个比上家大')
                    continue
                flag = 0 #结束循环
            bprint('###########经过人脑计算，当前玩家ID是', self.ID)
            bprint('#########选择的个数是', tNum)
            bprint('#########选择的点数是', tRoll)
            return tNum, tRoll

        lostRoll = lostR
        if self.tactics == 0:  # 保守策略
            if lnum == 0:  # 叫的点数数量为0，表示从自己开始第一个叫
                return self.decide_conser_start(playerNum)
            else:  # 有上家叫，先看是否开上家
                return self.decide_conser_ing( lnum, lroll, lostR)
        else: #  激进策略 todo 目前激进策略同保守，需完善
            if lnum == 0:  # 叫的点数数量为0，表示从自己开始第一个叫
                return self.decide_radical_start(playerNum)
            else:  # 有上家叫，先看是否开上家
                return self.decide_radical_ing( lnum, lroll, lostR)

    def return_dice(self):
        return self.diceValue

#todo
# done权重数组从game类挪到player类，每个player不能算自己叫过的权重
# done测试多人功能
# 加入数据记录功能
# done 加入人能玩的功能
# ing 激进策略 运行几百局看看不同策略胜率
# done一般不叫1点，叫了后其他人也叫一点
# done第一次叫的最小值，为在场人数 +1
# 目前叫时，如果出现数量相同的结果，加入权重计算时会计算所有点数，而不是只有最多数量的结果
# 游戏持续能玩，从上个输家开始叫



if __name__ == '__main__':
    playerNum  = int(input('请输入玩家总人数（不能超过5）:'))
    diceNum = 5

    gameNum = 1 # 当前游戏局数

    while(gameNum<=3):
        bprint('***********第几局游戏开始***********', gameNum)
        arrayPlayer = []
        #初始化Game和Player实例
        ins_Game = Game(playerNum, diceNum)
        for i in range(playerNum):
            #id;tac 0是保守，1是激进; nDice一局几个骰子; fPerson 0是机器，1是人类;lostRoll根据人数算的必输点数
            fPerson = 1 if i == 1 else 0 #加入一个人类玩家
            tPlayer = Player(i, 0 if i%2==1 else 1, diceNum, fPerson, ins_Game.lostRoll) #双数激进
            arrayPlayer.append(tPlayer)

        #游戏开始
        ins_Game.init_game(0)
        for i in range(playerNum):
            arrayPlayer[i].init_dice() # 掷骰子
            ins_Game.gather_roll(arrayPlayer[i].return_dice())
        ins_Game.count_roll()


        print("游戏开始###################################")
        roundNum = 1 # 当局游戏的第几个回合
        while(1):
            #上一次的数量和点数
            lNum, lRoll = ins_Game.return_last_call()
            # 叫的点数数量为0，表示从自己开始第一个叫
            curNum, curRoll = arrayPlayer[ins_Game.curPlayerID].decide(lNum, lRoll, ins_Game.return_lostRoll(), playerNum)

            # 更新每个玩家权重
            for i in range(playerNum):
                if not ins_Game.curPlayerID== arrayPlayer[i].return_ID() and not curRoll == 0:
                    arrayPlayer[i].update_weight(curRoll)
                #bprint('展示权重计算，player ID', i)
                #bprint('return_aWeight', arrayPlayer[i].return_aWeight())

            reslut = ins_Game.settle(curNum, curRoll)
            if not reslut == FALG_CONTINUE:
                # 游戏结束，result为输家ID
                bprint("游戏结束===LoserID is", reslut)
                gameNum += 1

                #释放所有对象 todo
                lPlayer = len(arrayPlayer)
                bprint('玩家数组长度', lPlayer)
                del arrayPlayer
                del ins_Game
                break
            bprint('************************一轮游戏结束，回合数(从1开始）是', roundNum)
            roundNum += 1
            #判断游戏是否结束同时更新数据


