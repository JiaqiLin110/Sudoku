#!/usr/bin/env python
# coding: utf-8

import numpy as np 
import pandas as pd
import pulp as plp

def solver(input_quiz):
    N = 9
    quiz = np.reshape([int(c) for c in input_quiz], (N,N))
    #print(quiz)
    prob = plp.LpProblem("Sudoku_Solver")
    objective = plp.lpSum(0)
    prob.setObjective(objective)
    
    rows = range(0,9)
    cols = range(0,9)
    grids = range(0,9)
    values = range(1,10)
    
    # Decision Variable/Target variable
    grid_vars = plp.LpVariable.dicts("grid_value", (rows,cols,values), cat='Binary')
    
    # CONSTRAINT 1: Constraint to ensure only one value is filled for a cell
    for row in rows:
        for col in cols:
                prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value] for value in values]),
                                        sense=plp.LpConstraintEQ, rhs=1, name=f"constraint_sum_{row}_{col}"))
    
    
    # CONSTRAINT 2: Constraint to ensure that values from 1 to 9 is filled only once in a row        
    for row in rows:
        for value in values:
            prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value]*value  for col in cols]),
                                        sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_row_{row}_{value}"))
    
    # CONSTRAINT 3: Constraint to ensure that values from 1 to 9 is filled only once in a column        
    for col in cols:
        for value in values:
            prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value]*value  for row in rows]),
                                        sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_col_{col}_{value}"))
    
    
    # CONSTRAINT 4: Constraint to ensure that values from 1 to 9 is filled only once in the 3x3 grid       
    for grid in grids:
        grid_row  = int(grid/3)
        grid_col  = int(grid%3)
    
        for value in values:
            prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[grid_row*3+row][grid_col*3+col][value]*value  for col in range(0,3) for row in range(0,3)]),
                                        sense=plp.LpConstraintEQ, rhs=value, name=f"constraint_uniq_grid_{grid}_{value}"))
    
    for row in rows:
            for col in cols:
                if(quiz[row][col] != 0):
                    prob.addConstraint(plp.LpConstraint(e=plp.lpSum([grid_vars[row][col][value]*value  for value in values]),
                                            sense=plp.LpConstraintEQ, 
                                            rhs=quiz[row][col], 
                                            name=f"constraint_prefilled_{row}_{col}"))
                    # Code to extract the final solution grid
                    
    prob.solve(plp.PULP_CBC_CMD(msg=False))
    
    
    result = ""
    if plp.LpStatus[prob.status]=='Optimal':
        solution = [[0 for col in cols] for row in rows]
        grid_list = []
        for row in rows:
            for col in cols:
                for value in values:
                    if plp.value(grid_vars[row][col][value]):
                        solution[row][col] = value 
                        
                        
        m = np.reshape(solution, (N*N,))
        for number in m:
            result+=str(number)

    return result


# In[4]:


# We test the following algoritm on small data set.
data1 = pd.read_csv("large1.csv") 
data2 = pd.read_csv("large2.csv") 
data = pd.concat([data1, data2])
data = data.reset_index(drop=True)

corr_cnt = 0

random_seed = 42
np.random.seed(random_seed)

if len(data) > 1000:
    samples = np.random.choice(len(data), 1000)
else:
    samples = range(len(data))

total = 0
correct = 0
for i in range(len(samples)):
    try:
        quiz = data["quizzes"][samples[i]]
        solu = data["solutions"][samples[i]]
        result = solver(quiz)
        #print(result)
        #print(result==solu)
        if result==solu:
            correct += 1
    except Exception as e:
        print(str(e))
    total += 1

print('Total number of puzzles: ', total)
print('Correctly solved number of puzzles: ', correct)
print('The success ratio:', correct/total)
