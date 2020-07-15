# Algorithm 3 presented in paper "Applyint MILP Method to Searching Integral 
# Distinguishers based on Division Property for 6 Lightweight Block Ciphers"
# Regarding to the paper, please refer to https://eprint.iacr.org/2016/857
# For more information, feedback or questions, pleast contact at xiangzejun@iie.ac.cn

# Implemented by Xiang Zejun, State Key Laboratory of Information Security, 
# Institute Of Information Engineering, CAS
import itertools
from myu2 import Myu2

if __name__ == "__main__":

	ROUND = int(input("Input the target round number: "))
	while not (ROUND > 0):
		print("Input a round number greater than 0.")
		ROUND = int(input("Input the target round number again: "))
        #combination
		
	#l=[0,1,2,3]
	#a=list(itertools.combinations(l,2))

	U_Min=[64]
	

	for i1 in range(63):
		Input=0xffffffffffffffff
		Input^=(0x1<<i1)
		myu2 = Myu2(ROUND,Input,U_Min)

		myu2.MakeModel()

		myu2.SolveModel()
