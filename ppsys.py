import psycopg2
import numpy as np
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

def get_error(sensitivity, epsilon):
    return 2 * (sensitivity / pow(epsilon, 2))





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
    q = "select * from (select company, product, count(*) ct from complaints group by company, product) where ct > 200"
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
    q = "with X as (select subproduct, count(*) ct from complaints group by subproduct) select * from X order by ct desc limit 10"
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

def run_queries(c, noise=0):

    for i in range(1, 6):
        #create file to log runtimes
        fname = "runtime_q"+str(i)
        if noise==1:
            fname+=str("noisy")
        fname+=".txt"
            
        f = open(fname, "w")
        f.write("Query number "+ str(i)+"\n")
        q = eval("getQ"+str(i)+"()")
        
        runtime_lst = []
        for j in range(10):
            st = time.time()
            c.execute(q)
            et = time.time()
            runtime_lst.append(et-st)
        f.write(str(runtime_lst))
        f.close()
        
            
        
    

def main():
    #establishing the connection
    conn = psycopg2.connect(
    database="cc151", user='postgres', password='1908', host='127.0.0.1', port= '5433'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    
    run_queries(cursor)
    
   
    """ cursor.execute(getQ1())
    data = cursor.fetchall()
    print("Output of Q1: ", len(data))
    
    cursor.execute(getQ2())
    data = cursor.fetchall()
    print("Output of Q2: ", len(data))
    
    cursor.execute(getQ3())
    data = cursor.fetchall()
    print("Output of Q3: ", len(data))
    
    cursor.execute(getQ4())
    data = cursor.fetchall()
    print("Output of Q4: ", len(data))
    
    cursor.execute(getQ5())
    data = cursor.fetchall()
    print("Output of Q5: ", len(data)) """

    listCounts = [233, 234, 556, 10, 20, 300, 700]
    print("BEFORE: " + str(listCounts))
    listCounts += laplace_mechanism(1, 0.632, len(listCounts))
    roundedCounts = [round(elem) for elem in listCounts]
    print("AFTER: " + str(roundedCounts))

    #Closing the connection
    conn.close()
    
if __name__=='__main__':
    main()
    