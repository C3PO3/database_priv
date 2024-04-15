import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import statistics
import time
import math

'''
Assume there is a list of queries.
1. Connect to a postgres server
2. For each query, run it without noise.
3. For each query, run it with noise 10 times with the same pre-determined privacy budget.
'''

# Function to get noise vector using sensetivity of 1
def laplace_mechanism(sensitivity, epsilon, data_size):
    b = sensitivity / epsilon
    noise = np.random.laplace(0, b, data_size)
    return noise

def error_plot(vecX, vecY, num):
    plt.figure(figsize=(8, 6))  # Adjust figure size as needed
    plt.scatter(vecX, vecY, color='b', label='Data Points')
    plt.xlabel('Epsilon Value')
    plt.ylabel('Error')
    plt.title('Query ' + str(num))
    plt.grid(True)
    plt.legend()
    plt.show()

def error_plot_given_counts(listCounts, query_num):
    # plot the error of each query given x and y vector
    vecY10 = []
    vecX = []
    vecY = 0
    for val in range(1, 11):
        for ep in range(1, 11):
            listCounts += laplace_mechanism(1, float(ep)/100.0, len(listCounts)) #0.632
            noisyData = [round(elem) for elem in listCounts]
            vecY += statistics.variance(noisyData)
        vecY10.append(vecY/10)
        vecX.append(float(val) / 100.0)
    error_plot(vecX, vecY10, query_num)

def add_noise(listCounts,eps):
    noisyData = listCounts.copy()
    noisyData += laplace_mechanism(1, eps, len(listCounts)) #0.632
    noisyData = [round(elem) for elem in noisyData]
    return noisyData
    
def getQ1():
    """
    returns string form of sql query
    for the question
    'Which company and product pairs have >200 complaints
    associated with them in the databse?'
    
    Returns:
        string : sql query
    """
    # Query 1
    q = "select * from (select company, product, count(*) ct from complaints group by company, product) where ct > 100"
    return q

def getQ2():
    """returns string form of sql query
    for the question
    'Which 10 subproduct have the highest number of complaints
    associated with them in the databse?'

    Returns:
        string : sql query
    """
    # Query 2
    q = "with X as (select subproduct, count(*) ct from complaints group by subproduct) select * from X order by ct desc"
    return q

def getQ3():
    """returns string form of sql query
    for the question
    'Which companies can MA 
    customers purchase credit reporting sevices from?'

    Returns:
        string : sql query
    """
    # Query 3
    q = "with Z as (with X as (select distinct company, state, count(*) ct from complaints where subproduct=' Credit reporting' group by company, state) select X.company, X.state, cast(X.ct as decimal)/cast(Y.ct as decimal) rat from X, (select distinct company, state, count(*) ct from complaints group by company, state)Y where X.company=Y.company and X.state=Y.state) select company, state, rat from Z where rat < 0.2 and state=' MA'"
    return q

def getQ4():
    """returns string form of sql query
    for the question
    'Which companies can FL 
    customers purchase credit reporting sevices from?'

    Returns:
        string : sql query
    """
    # Query 4
    q = "with Z as (with X as (select distinct company, state, count(*) ct from complaints where subproduct=' Credit reporting' group by company, state) select X.company, X.state, cast(X.ct as decimal)/cast(Y.ct as decimal) rat from X, (select distinct company, state, count(*) ct from complaints group by company, state)Y where X.company=Y.company and X.state=Y.state) select company, state, rat from Z where rat < 0.2 and state=' FL'"
    return q

def getQ5():
    """returns string form of sql query
    for the question
    'Which companies can TX 
    customers purchase credit reporting sevices from?'

    Returns:
        string : sql query
    """
    # Query 5
    q = "with Z as (with X as (select distinct company, state, count(*) ct from complaints where subproduct=' Credit reporting' group by company, state) select X.company, X.state, cast(X.ct as decimal)/cast(Y.ct as decimal) rat from X, (select distinct company, state, count(*) ct from complaints group by company, state)Y where X.company=Y.company and X.state=Y.state) select company, state, rat from Z where rat < 0.2 and state=' TX'"
    return q

    
def get_runtimes(c, noise=0):
    eps_lst = [0.01, 0.02, 0.03, 0.04, 0.05]
    for i in range(1, 6):
        count_idx = 2
        if (i==2):
            count_idx = 1
        #create file to log runtimes
        fname = "runtime_q"+str(i)
        if noise==1:
            fname+=str("noisy")
        fname+=".txt"
            
        f = open(fname, "w")
        f.write("Query number "+ str(i)+"\n")
        if noise==1:
            f.write("Each list corresponds to one epsilon value in the order following order: \n")
            f.write(str(eps_lst)+"\n")
        q = eval("getQ"+str(i)+"()")
        
        runtime_lst = []
        
        if noise==1:
            for eps in eps_lst:
                for j in range(10):
                    st = time.time()
                    c.execute(q)
                    listCounts = [el[count_idx] for el in c.fetchall()]
                    add_noise(listCounts, eps)
                    et = time.time()
                    runtime_lst.append(et-st)
                f.write(str(runtime_lst)+"\n\n")
                runtime_lst = []
        
        else:
            for j in range(10):
                st = time.time()
                c.execute(q)
                et = time.time()
                runtime_lst.append(et-st)
    
            f.write(str(runtime_lst)+"\n\n")
            
        f.close()

        
def test_noise():
    Q1_counts = [12, 134, 454, 235, 142]
    Q2_counts = [12, 134, 454, 235, 142]
    Q3_counts = [12, 134, 454, 235, 142]
    Q4_counts = [12, 134, 454, 235, 142]
    Q5_counts = [12, 134, 454, 235, 142]

    error_plot_given_counts(Q1_counts, 1)
    error_plot_given_counts(Q2_counts, 2)
    error_plot_given_counts(Q3_counts, 3)
    error_plot_given_counts(Q4_counts, 4)
    error_plot_given_counts(Q5_counts, 5)

def getQ1Q2Error():
    # make Q1 error graph

    rawData1 = readFileGiveData("Q1vec.txt")
    error_plot_given_counts(rawData1, 1)
    rawData2 = readFileGiveData("Q2vec.txt")
    error_plot_given_counts(rawData2, 2)

def readFileGiveData(filename):
    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()

    # Convert lines to integers and create a vector
    data_vector = [int(line.strip()) for line in lines]
    return data_vector

def main():
    #establishing the connection
    conn = psycopg2.connect(
    database="cc151", user='postgres', password='1908', host='127.0.0.1', port= '5433'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    #get_runtimes(cursor, noise=0)
    #get_runtimes(cursor, noise=1)
    
    cursor.execute(getQ3())
    output = cursor.fetchall()
    f = open("Q3vec.txt", "w")
    f2 = open("Q3out.txt", "w")
    for el in output:
        f.write(str(el[2])+"\n")
        f2.write(str(el)+ "\n")
    f.close()
    f2.close()
    
    cursor.execute(getQ4())
    output = cursor.fetchall()
    f = open("Q4vec.txt", "w")
    f2 = open("Q4out.txt", "w")
    for el in output:
        f.write(str(el[2])+"\n")
        f2.write(str(el)+ "\n")
    f.close()
    f2.close()
    
    cursor.execute(getQ5())
    output = cursor.fetchall()
    f = open("Q5vec.txt", "w")
    f2 = open("Q5out.txt", "w")
    for el in output:
        f.write(str(el[2])+"\n")
        f2.write(str(el)+ "\n")
    f.close()
    f2.close()
    
    #getQ1Q2Error()

    """ rawData1 = readFileGiveData("Q1vec.txt")
    epsilon1 = math.sqrt((2*1)/statistics.variance(rawData1))
    print(epsilon1)
    rawData2 = readFileGiveData("Q2vec.txt")
    epsilon2 = math.sqrt((2*1)/statistics.variance(rawData2))
    print(epsilon2) """

    #Closing the connection
    conn.close()
    
if __name__=='__main__':
    main()
    