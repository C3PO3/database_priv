import psycopg2
import numpy as np
import matplotlib.pyplot as plt
import statistics

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



def main():
    #establishing the connection
    conn = psycopg2.connect(
    database="cc151", user='postgres', password='1908', host='127.0.0.1', port= '5433'
    )
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    #Executing an MYSQL function using the execute() method
    cursor.execute("select version()")
    
    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print("Connection established to: ",data)
    
    print(getQ1())
    cursor.execute(getQ1())
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
    print("Output of Q5: ", len(data))

    # plot the error of each query given x and y vector
    vecX = []
    vecY = []
    for ep in range(1, 11):
        vecX.append(ep / 10.0)
        listCounts = [233, 234, 556, 10, 20, 300, 700]
        print("BEFORE: " + str(listCounts))
        listCounts += laplace_mechanism(1, ep, len(listCounts)) #0.632
        noisyData = [round(elem) for elem in listCounts]
        print("AFTER: " + str(noisyData))
        vecY.append(statistics.variance(noisyData))
    error_plot(vecX, vecY, 1)
    # error_plot(vecX, vecY, 2)
    # error_plot(vecX, vecY, 3)
    # error_plot(vecX, vecY, 4)
    # error_plot(vecX, vecY, 5)

    #Closing the connection
    conn.close()
    
if __name__=='__main__':
    main()
    