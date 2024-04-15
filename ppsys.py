import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import statistics
import time

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
            listCounts += laplace_mechanism(1, ep, len(listCounts)) #0.632
            noisyData = [round(elem) for elem in listCounts]
            vecY += statistics.variance(noisyData)
        vecY10.append(vecY/10)
        vecX.append(float(val) / 10.0)
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
    q = "with Y as (select company, state, count(*) ct from complaints group by company, state) select X.company, X.state, Y.ct from Y, (select distinct company, state from complaints where subproduct!=' Credit reporting') X where X.company=Y.company and X.state=' MA' and Y.ct > (select avg(ct) from Y) and Y.ct < 13"
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
    q = "with Y as (select company, state, count(*) ct from complaints group by company, state) select X.company, X.state, Y.ct from Y, (select distinct company, state from complaints where subproduct!=' Credit reporting') X where X.company=Y.company and X.state=' FL' and Y.ct > (select avg(ct) from Y) and Y.ct < 13"
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
    q = "with Y as (select company, state, count(*) ct from complaints group by company, state) select X.company, X.state, Y.ct from Y, (select distinct company, state from complaints where subproduct!=' Credit reporting') X where X.company=Y.company and X.state=' TX' and Y.ct > (select avg(ct) from Y) and Y.ct < 13"
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
    
    get_runtimes(cursor, noise=0)
    get_runtimes(cursor, noise=1)
    
    """ cursor.execute(getQ2())
    output = cursor.fetchall()
    f = open("Q2vec.txt", "w")
    f2 = open("Q2out.txt", "w")
    for el in output:
        f.write(str(el[1])+"\n")
        f2.write(str(el)+ "\n")
    f.close()
    f2.close() """
    
   

    #Closing the connection
    conn.close()
    
if __name__=='__main__':
    main()
    