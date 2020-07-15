"""
x_i_63,x_i_62,....x_i_0 denote the input to the (i+1)-th round.
"""

from gurobipy import *

import time



class Myu2:
	def __init__(self, Round ,Input, U_Min):
		self.x_input=Input
		self.dist=""
		for i in range(64):
				if((self.x_input>>(63-i))&1==0):
						self.dist+="c"
				else:
						self.dist+="a"
				if(i%4==3):
						self.dist+=" "

		#integral order
		self.order=0
		for i in range(64):
                        self.order+=(self.x_input>>i)&1
                                
		#print(self.dist)
		self.Round = Round
		self.blocksize = 64
		
		self.filename_model = "Myu2_"+str(self.order)+"th_"+  str(self.Round) +"round_" +str(self.dist) + ".lp"
		self.filename_result = "result_"+str(self.order)+"th_"+  str(self.Round) +"round_" +str(self.dist) + ".txt"
		fileobj = open(self.filename_model, "w")
		fileobj.close()
		fileboj = open(self.filename_result, "w")
		fileobj.close()

		self.u_min=U_Min#manimum of "u"

	# Linear inequalities for the Myu2 Sbox(same to Present one)
	S_T=[
	[1, 1, 1, 1, -1, -1, -1, -1, 0],
	[-2, -2, -2, -4, 1, 4, 1, -3, 7],
	[0, 0, 0, -2, -1, -1, -1, 2, 3],
	[-2, -1, -1, 0, 3, 3, 3, 2, 0],
	[1, 1, 1, 1, -2, -2, 1, -2, 1],
	[0, 0, 0, 1, 1, -1, -2, -1, 2],
	[0, -1, -1, -2, 1, 0, 1, -1, 3],
	[0, 0, 0, 0, -1, 1, -1, 1, 1],
	[0, -2, -2, 0, 1, -1, 1, 2, 3],
	[0, 0, 0, -1, 1, 1, 1, 1, 0]
	]
	NUMBER = 9

	#make objective function
	def CreateObjectiveFunction(self):
		"""
		Create objective function of the MILP model
		"""
		fileobj = open(self.filename_model, "a")
		fileobj.write("Minimize\n")
		eqn = []
		for i in range(0,16):
			eqn.append("x3" + "_" + str(i) + "_" + str(self.Round))
		for i in range(0,16):
			eqn.append("x2" + "_" + str(i) + "_" + str(self.Round))
		for i in range(0,16):
			eqn.append("x1" + "_" + str(i) + "_" + str(self.Round))
		for i in range(0,16):
			eqn.append("x0" + "_" + str(i) + "_" + str(self.Round))

		temp = " + ".join(eqn)

		fileobj.write(temp)
		fileobj.write("\n")
		fileobj.close()

	#16bit permutation
	def VariablePermutaion(self, x):
		"""
		Bit Permutation.
		"""
		eqn = []
		permutation=[8, 5, 2, 15, 4, 1, 14, 11, 0, 13, 10, 7, 12, 9, 6, 3]
		for i in range(0,16):
			eqn.append(x[permutation[i]])
		return eqn


	def CreateConstrainsSplit(self,x_in, y_out1,y_out2):
		"""
		Generate constraints by split operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0,16):
			eqn = []
			eqn.append(x_in[i])
			eqn.append(y_out1[i])
			eqn.append(y_out2[i])
			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def CreateVariable(self, n, x):
		"""
		Generate variables used in the model.
		"""
		variable = []
		for i in range(0,16):
			variable.append(x + "_" + str(i) + "_" + str(n))
		return variable
        #S-Box Layer
	def ConstraintsBySbox(self, variable1, variable2):
		"""
		Generate the constraints by sbox layer.
		"""
		fileobj = open(self.filename_model,"a")
		for k in range(0,4):
			for coff in Myu2.S_T:
				temp = []
				for u in range(0,4):
					temp.append(str(coff[u]) + " " + variable1[(k * 4) + 3 - u])
				for v in range(0,4):
					temp.append(str(coff[v + 4]) + " " + variable2[(k * 4) + 3 - v])
				temp1 = " + ".join(temp)
				temp1 = temp1.replace("+ -", "- ")
				s = str(-coff[Myu2.NUMBER - 1])
				s = s.replace("--", "")
				temp1 += " >= " + s
				fileobj.write(temp1)
				fileobj.write("\n")
		fileobj.close();

	def CreateConstraintsXor(self,x_in1, x_in2,y_out):
		"""
		Generate the constraints by Xor operation.
		"""
		fileobj = open(self.filename_model, "a")
		for i in range(0, 16):
			eqn = []
			eqn.append(y_out[i])
			eqn.append(x_in1[i])
			eqn.append(x_in2[i])

			temp = " - ".join(eqn)
			temp = temp + " = " + str(0)
			fileobj.write(temp)
			fileobj.write("\n")
		fileobj.close()

	def Constraint(self):

		fileobj = open(self.filename_model, "a")
		fileobj.write("Subject To\n")
		fileobj.close()
		x3_in = self.CreateVariable(0,"x3")
		x2_in = self.CreateVariable(0,"x2")
		x1_in = self.CreateVariable(0,"x1")
		x0_in = self.CreateVariable(0,"x0")

		for i in range(0, self.Round):
			#set up variables
			x3_out = self.CreateVariable((i+1), "x3")
			x2_out = self.CreateVariable((i+1), "x2")
			x1_out = self.CreateVariable((i+1), "x1")
			x0_out = self.CreateVariable((i+1), "x0")
			al = self.CreateVariable(i, "al")
			bl = self.CreateVariable(i, "bl")
			cl = self.CreateVariable(i, "cl")
			dl = self.CreateVariable(i, "dl")
			el = self.CreateVariable(i, "el")			
			ar = self.CreateVariable(i, "ar")
			br = self.CreateVariable(i, "br")
			cr = self.CreateVariable(i, "cr")
			dr = self.CreateVariable(i, "dr")
			er = self.CreateVariable(i, "er")
			#make a constrains
			self.CreateConstrainsSplit(x3_in,al,x0_out)#copy (1)
			self.CreateConstrainsSplit(x1_in,ar,x2_out)#copy (2)
			self.CreateConstraintsXor(x2_in,self.VariablePermutaion(el),x3_out)#xor (1)
			self.CreateConstraintsXor(x0_in,self.VariablePermutaion(er),x1_out)#xor (2)
			self.ConstraintsBySbox(al,bl)
			self.ConstraintsBySbox(self.VariablePermutaion(bl),cl)
			self.ConstraintsBySbox(self.VariablePermutaion(cl),dl)
			self.ConstraintsBySbox(self.VariablePermutaion(dl),el)			
			self.ConstraintsBySbox(ar,br)
			self.ConstraintsBySbox(self.VariablePermutaion(br),cr)
			self.ConstraintsBySbox(self.VariablePermutaion(cr),dr)
			self.ConstraintsBySbox(self.VariablePermutaion(dr),er)
			#take over
			x3_in=x3_out
			x2_in=x2_out
			x1_in=x1_out
			x0_in=x0_out

	def BinaryVariable(self):
		"""
		Specify variable type.
		"""
		fileobj = open(self.filename_model, "a")
		fileobj.write("Binary\n")
		for i in range(0, self.Round):
			for j in range(0, 16):
				fileobj.write(("x3_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("x2_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("x1_"+ str(j) + "_"  + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("x0_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("al_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("bl_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("cl_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("dl_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("el_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("ar_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("br_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("cr_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("dr_" + str(j) + "_" + str(i)))
				fileobj.write("\n")
			for j in range(0, 16):
				fileobj.write(("er_" + str(j) + "_" + str(i)))
				fileobj.write("\n")

		for j in range(0, 16):
			fileobj.write(("x0_" + str(j) + "_" + str(self.Round)))
			fileobj.write("\n")
		for j in range(0, 16):
			fileobj.write(("x1_" + str(j) + "_" + str(self.Round)))
			fileobj.write("\n")
		for j in range(0, 16):
			fileobj.write(("x2_" + str(j) + "_" + str(self.Round)))
			fileobj.write("\n")			
		for j in range(0, 16):
			fileobj.write(("x3_" + str(j) + "_" + str(self.Round)))
			fileobj.write("\n")

		fileobj.write("END")
		fileobj.close()


	def Init(self):
		"""
		Generate constraints by the initial division property.
		"""


		fileobj = open(self.filename_model, "a")
		x3 = self.CreateVariable(0,"x3")
		x2 = self.CreateVariable(0,"x2")
		x1 = self.CreateVariable(0,"x1")
		x0 = self.CreateVariable(0,"x0")



		for i in range(0,16):
			fileobj.write((x3[15-i] + " = " + str((self.x_input>>(63-i))&1) ))
			fileobj.write("\n")
		for i in range(0,16):
			fileobj.write((x2[15-i] + " = " + str((self.x_input>>(47-i))&1) ))
			fileobj.write("\n")
		for i in range(0,16):
			fileobj.write((x1[15-i] + " = " + str((self.x_input>>(31-i))&1) ))
			fileobj.write("\n")
		for i in range(0,16):
			fileobj.write((x0[15-i] + " = " + str((self.x_input>>(15-i))&1) ))
			fileobj.write("\n")
		fileobj.close()

	def MakeModel(self):
		"""
		Generate the MILP model of Present given the round number and activebits.
		"""
		self.CreateObjectiveFunction()
		self.Constraint()
		self.Init()
		self.BinaryVariable()
	########################## I edited some points by using round() so that I let obj-values Round-off(sisyagonyu).
	def WriteObjective(self, obj):
		"""
		Write the objective value into filename_result.
		"""
		fileobj = open(self.filename_result, "a")
		#writing obj function
		fileobj.write("The objective value = %d\n" %round(obj.getValue()))
		eqn1 = []
		eqn2 = []
		for i in range(0, self.blocksize):
			u = obj.getVar(i)
			#Edit
			#if u.getAttr("x") != 0:#before
			if round(u.getAttr("x")) != 0:
				eqn1.append(u.getAttr('VarName'))
				#Edit
				#eqn2.append(u.getAttr('x'))#Before
				eqn2.append(round(u.getAttr('x')))
		length = len(eqn1)
		for i in range(0,length):
			s = eqn1[i] + "=" + str(eqn2[i])
			fileobj.write(s)
			fileobj.write("\n")
		fileobj.close()

	def SolveModel(self):
		"""
		Solve the MILP model to search the integral distinguisher of Present.
		"""
		time_start = time.time()
		m = read(self.filename_model)
		counter = 0
		set_zero = []
		global_flag = False
		while counter < self.blocksize:
			m.optimize()
			# Gurobi syntax: m.Status == 2 represents the model is feasible.
			if m.Status == 2:
				obj = m.getObjective()
				if round(obj.getValue()) > 1:
					global_flag = True
					break
				else:
					fileobj = open(self.filename_result, "a")
					fileobj.write("************************************COUNTER = %d\n" % counter)
					fileobj.close()
					self.WriteObjective(obj)
					for i in range(0, self.blocksize):
						u = obj.getVar(i)#Position of variable
						#Edit
						#temp = u.getAttr('x')#Value of variable#Before
						temp = round(u.getAttr('x'))#Value of variable
						if temp == 1:
							set_zero.append(u.getAttr('VarName'))
							u.ub = 0
							m.update()
							counter += 1
							break
			# Gurobi syntax: m.Status == 3 represents the model is infeasible.
			elif m.Status == 3:
				global_flag = True
				break
			else:
				print("Unknown error!")

                
                        
                        
		fileobj = open(self.filename_result, "a")
		if global_flag:
			fileobj.write("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher Found!\n\n")
			print("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher Found!\n")
			fileobj.close()

			#"""
			if(counter < self.u_min[0]):#If the number of "u" is Minimum,distinguisher is written to file.
				print("self.u_min : "+str(self.u_min))
				self.u_min[0]=counter#updating the minimum of "u"
				file_found = open("Best "+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher.txt","w")
				file_found.write("Initial : " + str(self.dist)+"\n")
				file_found.close()
                        #"""
		else:
			fileobj.write("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher do NOT exist\n\n")
			print("\n"+str(self.order)+"th_"+str(self.Round)+"round_Integral Distinguisher do NOT exist\n")
			fileobj.close()

		fileobj = open(self.filename_result, "a")
		fileobj.write("Those are the coordinates set to zero: \n")
		for u in set_zero:
			fileobj.write(u)
			fileobj.write("\n")
		fileobj.write("\n")
		time_end = time.time()
		fileobj.write(("Time used = " + str(time_end - time_start)))
		#now we use set_zero
		dist_array=["b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",
                          "b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",
                          "b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",
                          "b","b","b","b","b","b","b","b","b","b","b","b","b","b","b","b",]
		fileobj.write("\n"+str(self.order)+"th_"+str(self.Round)+"round_integral distinguisher\n")
		for u in set_zero:
			if(u[4]=="_"):
				dist_array[int(u[1:2])*16+int(u[3:4])]="u"
			else:
				dist_array[int(u[1:2])*16+int(u[3:5])]="u"
		dist_out=""
		for u in range(64):
			dist_out+=dist_array[63-u]
			if(u%4==3):
				dist_out+=" "
		fileobj.write(dist_out)
		fileobj.close()
