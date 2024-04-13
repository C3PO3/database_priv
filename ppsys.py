import psycopg2
import numpy as np

# Function to get noise vector using sensetivity of 1
def laplace_mechanism(sensitivity, epsilon, data_size):
    b = sensitivity / epsilon
    noise = np.random.laplace(0, b, data_size)
    return noise

def get_error(sensitivity, epsilon):
    return 2 * (sensitivity / pow(epsilon, 2))




'''
Assume there is a list of queries.
1. Connect to a postgres server
2. For each query, run it without noise.
3. For each query, run it with noise 10 times with the same pre-determined privacy budget.
'''
def getQ1():
    """
    returns string form of sql query
    for the question
    'Which company and product pairs have >200 complaints
    associated with them in the databse?'
    """
    q = "select * from (select company, product, count(*) ct from complaints group by company, product) where ct > 200"
    return q

def getQ2():
    # Query 2
    q = ""
    return q

def getQ3():
    # Query 3
    q = ""
    return q

def getQ4():
    # Query 4
    q = ""
    return q

def getQ1():
    # Query 5
    q = ""
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
    
    cursor.execute("select * from (select company, product, count(*) ct from complaints group by company, product) where ct > 200")
    data = cursor.fetchall()
    print("Output of Q1: ", len(data))

    listCounts = [233, 234, 556, 10, 20, 300, 700]
    print("BEFORE: " + str(listCounts))
    listCounts += laplace_mechanism(1, 0.632, len(listCounts))
    roundedCounts = [round(elem) for elem in listCounts]
    print("AFTER: " + str(roundedCounts))

    #Closing the connection
    conn.close()
    
if __name__=='__main__':
    main()
    