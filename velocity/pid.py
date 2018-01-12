##
## @file pid.py
## @brief Return velocity after applying PID
##
import rospy
import numpy as np
#import matplotlib.pyplot as plt
import time

import sys

from utils.config import *
from utils.geometry import *

dt = 0.001

# try:
# 	f = open("pid_img/values/pid.txt",'a')
# except:
# 	f = open("pid_img/values/pid.txt",'w')




# pid_tu = rospy.Publisher('pid_c', pid_tune, queue_size=10)

##
## @brief      PID on velocity vx,vy
##
## @param      vX         velocity in x
## @param      vY         velocity in y
## @param      errorInfo  The error information
## @param      pso        Particle Swarm Optimiser object
## 
## @see        error.py
##
##
## @return     Velocity after PID
##
# i = 0
def pid(vX,vY,errorInfo,pso=None):
	global f
	errorPX = errorInfo.errorX
	errorPY = errorInfo.errorY
	errorIX = errorInfo.errorIX + errorPX
	errorIY = errorInfo.errorIY + errorPY
	errorDX = (errorPX - errorInfo.lastErrorX)/dt
	errorDY = (errorPY - errorInfo.lastErrorY)/dt
	errorX = np.array([errorPX,errorIX,errorDX])
	errorY = np.array([errorPY,errorIY,errorDY])
	# print(pso.__dict__)
	pso.error_in_x.append(errorPX)
	pso.error_in_y.append(errorPY)
	if pso==None or 1:
		# k = np.array([0,0,0]) 		#define k
		k = np.array([3.5,0.00001,0.0003])
		print("Errors X",errorX)
		deltaVX = errorX.dot(k)
		deltaVY = errorY.dot(k)
		if pso.should_save_data:
			print("Data saved")
			np.savetxt("bot_tune/data_check.txt",pso.error_in_x)
			np.savetxt("bot_tune/data_check.txt",pso.error_in_y)
			sys.exit(0)
		vX = vX + deltaVX
		vY = vY + deltaVY
		errorInfo.errorIX = errorInfo.errorIX + errorInfo.errorX
		errorInfo.errorIY = errorInfo.errorIY + errorInfo.errorY
		errorInfo.lastErrorX = errorInfo.errorX
		errorInfo.lastErrorY = errorInfo.errorY
		return vX,vY

	# Optimiser (PSO)
	else:
		currIter = pso.currIter
		p = pso.currParticle
		currMove = pso.swarm[p].move
		maxMoves = pso.maxMoves
		numParticles = pso.numParticles
		maxIter = pso.maxIter

		k = pso.swarm[p].k
		# pid_tune = pid_tune()
		# pid_tune.pc = k[0]
		# pid_tune.ic = k[1]
		# pid_tune.dc = k[2]
		# pid_tu.publish(pid_tune)
		# print("pid constants ", k)

		deltaVX = errorX.dot(k)
		deltaVY = errorY.dot(k)

		vX = vX + deltaVX
		vY = vY + deltaVY

		errorMagnitude = np.linalg.norm(np.array([errorPX,errorPY]))
		pso.swarm[p].currErrorSum += errorMagnitude


		errorInfo.errorIX = errorInfo.errorIX + errorInfo.errorX
		errorInfo.errorIY = errorInfo.errorIY + errorInfo.errorY
		errorInfo.lastErrorX = errorInfo.errorX
		errorInfo.lastErrorY = errorInfo.errorY

		pso.swarm[p].move = (currMove + 1)%maxMoves
		pso.lastTime = time.time()
		pso.errors.append(errorPX)
		# print("Current Move", currMove)
		if pso.swarm[p].move == 0:
			if pso.swarm[p].currErrorSum <= pso.swarm[p].minLocalError:
				pso.swarm[p].minLocalError = pso.swarm[p].currErrorSum
				pso.swarm[p].bestLocalK = k

			if pso.swarm[p].currErrorSum <= pso.minGlobalError:
				pso.minGlobalError = pso.swarm[p].currErrorSum
				pso.bestGlobalK = k

			pso.swarm[p].currErrorSum = 0 ##For next iteration
			r1 = np.random.rand()
			r2 = np.random.rand()
			pso.swarm[p].v = pso.omega*pso.swarm[p].v + pso.c1*r1*(pso.swarm[p].bestLocalK - k) + pso.c2*r2*(pso.bestGlobalK - k)
			pso.swarm[p].k = k + pso.swarm[p].v
			pso.currParticle = (p+1)%numParticles
			# print("Particle #", pso.currParticle)
			if pso.currParticle == 0:
				pso.currIter = currIter + 1
				# print("Current Iteration #", pso.currIter)





		return vX,vY
