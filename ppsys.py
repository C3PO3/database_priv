import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import statistics
import time
import math
import ast

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

def spread_plot(vecX, vecY, qnum, num):
    plt.figure(figsize=(8, 6))  # Adjust figure size as needed
    #plt.scatter(vecX, vecY, color='b', label='Data Points')
    plt.plot(vecX, vecY, '-o')
    plt.xlabel('Execution number')
    plt.ylabel('Average count')
    plt.title('Epsilon ' + str(num))
    plt.grid(True)
    plt.legend()
    #plt.show()
    plt.savefig("SpQ"+str(qnum)+"Eps"+str(num)+".png")

def makeSpreadPlot(rawData,qnum):
    epsilons = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    executions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    yAxis = []
    avg = 0
    for epsilon in epsilons:
        for execution in executions:
            noisyData = laplace_mechanism(1, epsilon, len(rawData)) + rawData
            noisyData = [round(elem) for elem in noisyData]
            for num in noisyData:
                avg += num
            avg /= len(noisyData)
            yAxis.append(avg)
            avg = 0
        spread_plot(executions, yAxis, qnum, epsilon)
        yAxis = []

def error_plot(vecX, vecY, num):
    plt.figure(figsize=(8, 6))  # Adjust figure size as needed
    #plt.scatter(vecX, vecY, color='b', label='Data Points')
    plt.plot(vecX, vecY, '-o')
    plt.xlabel('Epsilon Value')
    plt.ylabel('Error')
    plt.title('Query ' + str(num))
    plt.grid(True)
    plt.legend()
    #plt.show()
    plt.savefig("ErrorQ"+str(num)+".png")

def error_plot_given_counts(listCounts, query_num):
    # plot the error of each query given x and y vector
    vecY10 = []
    vecX = []
    vecY = 0
    reset = listCounts
    for ep in range(1, 11):
        for val in range(1, 11):
            listCounts += laplace_mechanism(1, float(ep)/100.0, len(listCounts)) #0.632
            noisyData = [round(elem) for elem in listCounts]
            vecY += statistics.variance(noisyData)
            listCounts = reset
        vecY10.append(vecY/10)
        vecX.append(float(ep) / 100.0)
        vecY = 0
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
    q = "with Z as (with X as (select distinct company, state, zip_code, count(*) ct from complaints where subproduct=' Credit reporting' group by company, state, zip_code) select X.company, X.state, X.zip_code, cast(X.ct as decimal)/cast(Y.ct as decimal) rat from X, (select distinct company, state, zip_code, count(*) ct from complaints group by company, state, zip_code)Y where X.company=Y.company and X.state=Y.state and X.zip_code=Y.zip_code) select company, state, zip_code, rat from Z where rat < 0.2 and state=' MA'"
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
    q = "with Z as (with X as (select distinct company, state, zip_code, count(*) ct from complaints where subproduct=' Credit reporting' group by company, state, zip_code) select X.company, X.state, X.zip_code, cast(X.ct as decimal)/cast(Y.ct as decimal) rat from X, (select distinct company, state, zip_code, count(*) ct from complaints group by company, state, zip_code)Y where X.company=Y.company and X.state=Y.state and X.zip_code=Y.zip_code) select company, state, zip_code, rat from Z where rat < 0.2 and state=' FL'"
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
    q = "with Z as (with X as (select distinct company, state, zip_code, count(*) ct from complaints where subproduct=' Credit reporting' group by company, state, zip_code) select X.company, X.state, X.zip_code, cast(X.ct as decimal)/cast(Y.ct as decimal) rat from X, (select distinct company, state, zip_code, count(*) ct from complaints group by company, state, zip_code)Y where X.company=Y.company and X.state=Y.state and X.zip_code=Y.zip_code) select company, state, zip_code, rat from Z where rat < 0.2 and state=' TX'"
    return q

def get_query_outputs(cursor, query_list=[1, 2, 3, 4, 5]):
    count_idx = 2
    for qnum in query_list:
        # identify index of output where the main count will be 
        if qnum==2:
            count_idx = 1
        if qnum>2:
            count_idx = 3
        
        # run the query
        cursor.execute(eval("getQ"+str(qnum)+"()"))
        response = cursor.fetchall()
        
        # open files to:
        # 1. store whole row
        # 2. store just the count
        f1 = open("Q"+str(qnum)+"out.txt", "w")
        f2 = open("Q"+str(qnum)+"vec.txt", "w")
        
        for el in response:
            f1.write(str(el)+"\n")
            f2.write(str(el[count_idx])+"\n")
        
        f1.close()
        f2.close()
    
def runtime_plot(vecX, vecY, num):
    plt.figure(figsize=(8, 6))  # Adjust figure size as needed
    #plt.scatter(vecX, vecY, color='b', label='Data Points')
    plt.plot(vecX, vecY, '-o')
    plt.xlabel('Epsilon Value')
    plt.ylabel('Runtime')
    plt.title('Query ' + str(num))
    plt.grid(True)
    plt.legend()
    #plt.show()
    plt.savefig('RuntimePlotQ'+str(num)+'.png')

# def runtime_plot_given_counts(rawData, query_num):

def read_runtime(filename, query):
    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()
    epsilons = ast.literal_eval(lines[2])
    averageTimes = []

    for val in range(0, len(lines)):
        num = 0
        if((val >= 3) and (val % 2 == 1)):
            list = ast.literal_eval(lines[val])
            for item in list:
                num += item
            num /= len(list)
            averageTimes.append(num)
            num = 0
    runtime_plot(epsilons, averageTimes, query)


def get_runtimes(c, noise=0):
    eps_lst = [0.01, 0.02, 0.03, 0.04, 0.05]
    count_idx = 2
    for i in range(1, 6):
        if (i==2):
            count_idx = 1
        if (i>2):
            count_idx=3
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
                    listCounts = [float(str(el[count_idx])) for el in c.fetchall()]
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

def error_plot_given_counts_345(listCounts, query_num):
    # plot the error of each query given x and y vector
    vecY10 = []
    vecX = []
    vecY = 0
    reset = listCounts
    noisyData = []
    for ep in range(1, 11):
        for val in range(1, 11):
            listCounts += laplace_mechanism(1, float(ep)/100.0, len(listCounts)) #0.632
            for elem in listCounts:
                if(elem > 1):
                    elem = 1
                elif(elem < 0):
                    elem = 0
                noisyData.append(elem)
            vecY += statistics.variance(noisyData)
            listCounts = reset
            noisyData = []
        vecY10.append(vecY/10)
        vecX.append(float(ep) / 100.0)
        vecY = 0
    error_plot(vecX, vecY10, query_num)

def getQ345Error():
    rawData3 = readFileGiveData("Q3vec.txt")
    error_plot_given_counts_345(rawData3, 3)
    rawData4 = readFileGiveData("Q4vec.txt")
    error_plot_given_counts_345(rawData4, 4)
    rawData5 = readFileGiveData("Q5vec.txt")
    error_plot_given_counts_345(rawData5, 5)

def readFileGiveData(filename):
    with open(filename, 'r') as file:
        # Read lines from the file
        lines = file.readlines()

    # Convert lines to integers and create a vector
    data_vector = [float(line.strip()) for line in lines]
    return data_vector

def main():
    #establishing the connection
    conn = psycopg2.connect(
    database="cc151", user='postgres', password='1908', host='127.0.0.1', port= '5433')
    # #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # A.
    # run a given list of queries
    # runs all five queries of list of query numbers are not provided
    """ get_query_outputs(cursor) """
    
    # B.
    # get run times with and without noise addition
    # do 10 trials for each query 
    # and for each epsilon in the case of noise addition
    """ get_runtimes(cursor, noise=0)
    get_runtimes(cursor, noise=1) """
    # plot the runtimes
    """ for query_num in range(1,6):
        read_runtime("runtime_q"+str(query_num)+"noisy.txt", query_num) """

    #Closing the connection
    conn.close()

    
    # run to get error graphs
    """ getQ1Q2Error()
    getQ345Error() """
    
    # run to get plot of spread of query response values for each epsilon
    for query_num in range(1,6):
        rawData = readFileGiveData("Q"+str(query_num)+"vec.txt")
        makeSpreadPlot(rawData, query_num)

    # run to look at best epsilon for Q1 and Q2
    """ rawData1 = readFileGiveData("Q1vec.txt")
    epsilon1 = math.sqrt((2*1)/statistics.variance(rawData1))
    print(epsilon1)
    rawData2 = readFileGiveData("Q2vec.txt")
    epsilon2 = math.sqrt((2*1)/statistics.variance(rawData2))
    print(epsilon2) """


if __name__=='__main__':
    main()
